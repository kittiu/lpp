import frappe # type: ignore
import json
from frappe import _, msgprint
from frappe.utils import (
    get_link_to_form,
    nowdate,
)
from erpnext.manufacturing.doctype.work_order.work_order import validate_operation_data, split_qty_based_on_batch_size, WorkOrder

class CustomWorkOrder(WorkOrder):
    # ตอน Submit Work Order เอาฟังก์ชัน create_job_card ออก ตรวจสอบแล้วใช้แค่ตอน on_submit ไม่มีเรียกใช้ที่อื่น (เขียนให้ pass ไว้เฉยๆ ไม่มีการทำงานข้างใน)
    def create_job_card(self):
        pass

@frappe.whitelist()
def get_jobcard_remaining(data):
    data = ensure_json(data)  # Ensure data is parsed once

    # ตรวจสอบว่าค่าที่ใช้เป็น int/float หรือแปลงให้ถูกต้องก่อนคำนวณ
    try:
        count_amount = int(data['custom_total_run_cards'])  # แปลงเป็น int
    except ValueError:
        frappe.throw("custom_total_run_cards ต้องเป็นตัวเลข")

    job_cards = frappe.db.get_all(
        'Job Card',
        filters={
            'work_order': data['name'],
            'custom_runcard_no': ['!=', None],  # เพิ่มเงื่อนไข where เพื่อกรองค่า None
        },
        fields=['custom_runcard_no', 'operation'],
    )

    count_jobcard = len(job_cards)
    count_operations = len(data['operations'])

    # ตรวจสอบว่าจำนวน operations ต้องไม่เป็น 0 เพื่อหลีกเลี่ยงการหารด้วยศูนย์
    if count_operations == 0:
        frappe.throw("ไม่พบ operations สำหรับการคำนวณ")

    # คำนวณผลลัพธ์โดยแปลงค่าเป็น float เพื่อป้องกันปัญหาในการหาร
    result = float(count_amount) - (count_jobcard / count_operations)

    # ปัดผลลัพธ์ให้มีทศนิยม 2 ตำแหน่ง
    result = round(result, 2)

    return result

@frappe.whitelist()
def get_item_molds(item_code):
    # Get the child table records from the Item DocType
    molds = frappe.get_all("Item Molds Detail", 
    filters={'parent': item_code},  # Parent is the Item
    fields=['item_code', 'item_name', 'mold_id'])  # Adjust fields to match your child table fields
    return molds

@frappe.whitelist()
def make_job_card(work_order, operations):
    work_order = ensure_json(work_order)
    operations = ensure_json(operations)
    
    if len(operations) > 1:
        msgprint(_("Only one row is allowed in the Operations table."))
        return

    if work_order['custom_jobcard_remaining'] and work_order['custom_total_run_cards']:
        operations_in_work_order = work_order['operations']
        amount = work_order['custom_total_run_cards']
        work_order = frappe.get_doc("Work Order", work_order['name'])
        custom_quantity__run_card = int(work_order.custom_quantity__run_card)

        job_card_creation_list = []  
        validation_failed = False

        for row in operations:
            row = frappe._dict(row)
            validate_operation_data(row)
            qty = row.get("qty")
            if not qty:
                continue
            
            # Fetch existing job cards related to the operation
            get_job_cards = frappe.db.get_all(
                'Job Card', 
                filters={
                    'work_order': work_order.name, 
                    'operation': row.operation,
                    'custom_runcard_no': ['!=', None],
                },
                fields=['custom_runcard_no', 'for_quantity'],
            )

            # Aggregate job cards by runcard number
            aggregated_results = {}
            for card in get_job_cards:
                card_key = card['custom_runcard_no']
                record = aggregated_results.setdefault(card_key, {'custom_runcard_no': card_key, 'for_quantity': 0, 'number': 0})
                record['for_quantity'] += card['for_quantity']
                record['number'] += 1

            job_cards = list(aggregated_results.values())

            # Determine max run card number and initialize runcard_no
            max_runcard_no = count_distinct_runcard_no(job_cards)
            runcard_no = f"{max_runcard_no or 1}/{amount}"

            # Filter job cards to get only those matching the current runcard_no
            filtered_job_cards = [job_card for job_card in get_job_cards if job_card['custom_runcard_no'] == runcard_no]

            # Find the current operation's index
            operation_no = next((op['idx'] for op in operations_in_work_order if op['name'] == row['name']), None)

            prev_total = 0
            if operation_no and operation_no > 1:
                prev_operation_name = next(
                    (op['operation'] for op in operations_in_work_order if op['idx'] == operation_no - 1), None
                )
                if prev_operation_name:
                    prev_operation = frappe.db.get_all(
                        'Job Card',
                        filters={
                            'work_order': 'WO2411-0006',  # Consider dynamic filter here
                            'operation': prev_operation_name,
                            'custom_runcard_no': runcard_no,
                        },
                        fields=['custom_runcard_no', 'SUM(total_completed_qty) as total_completed_qty'],
                        group_by='custom_runcard_no'
                    )
                    prev_total = prev_operation[0]['total_completed_qty'] if prev_operation else 0
            
            # Validate the job card and prepare for creation
            total = sum(card['for_quantity'] for card in filtered_job_cards)
            if custom_quantity__run_card == total and custom_quantity__run_card >= qty:
                # Prepare for the next run card
                runcard_no = f"{max_runcard_no + 1}/{amount}"
                sequence = 1
                job_card_creation_list.append((work_order, row, qty, runcard_no, sequence, len(operations_in_work_order), operation_no))
            
            elif prev_total == total and custom_quantity__run_card >= qty:
                # Prepare for the next run card if previous total matches
                runcard_no = f"{max_runcard_no + 1}/{amount}"
                sequence = 1
                job_card_creation_list.append((work_order, row, qty, runcard_no, sequence, len(operations_in_work_order), operation_no))

            elif custom_quantity__run_card >= (total + qty):
                # Add data for the current run card
                sequence = len(filtered_job_cards) + 1
                job_card_creation_list.append((work_order, row, qty, runcard_no, sequence, len(operations_in_work_order), operation_no))
            
            else:
                # Validation failed
                msgprint(_(f"จำนวนสั่งผลิตมากเกินกว่าจำนวนต่อ Runcard ({row.operation})"))
                validation_failed = True
                break  # Exit loop on validation failure

        # Process job cards only if all rows passed validation
        if not validation_failed and job_card_creation_list:
            for job_card_data in job_card_creation_list:
                process_job_card_creation(*job_card_data)

    else:
        msgprint(_('จำนวน Runcard เกินกว่าที่กำหนด'))


def process_job_card_creation(work_order, row, qty, runcard_no, sequence=1, total_operation=1, operation_no=1):
    while qty > 0:
        qty = split_qty_based_on_batch_size(work_order, row, qty)
        if row.job_card_qty > 0:
            create_job_card(work_order, row, runcard_no, sequence, total_operation, operation_no, auto_create=True)


def create_job_card(work_order, row, runcard_no, sequence, total_operation, operation_no, enable_capacity_planning=False, auto_create=False):
    doc = frappe.new_doc("Job Card")
    doc.update(
        {
            "work_order": work_order.name,
            "workstation_type": row.get("workstation_type"),
            "operation": row.get("operation"),
            "workstation": row.get("workstation"),
            "posting_date": nowdate(),
            "for_quantity": row.job_card_qty or work_order.get("qty", 0),
            "operation_id": row.get("name"),
            "bom_no": work_order.bom_no,
            "project": work_order.project,
            "company": work_order.company,
            "sequence_id": row.get("sequence_id"),
            "wip_warehouse": work_order.wip_warehouse,
            "hour_rate": row.get("hour_rate"),
            "serial_no": row.get("serial_no"),
            "custom_runcard_no": runcard_no,
            "custom_sequence": sequence,
            "custom_workstation_details": row.get("operation"),
            "custom_machine": row.get("workstation"),
            "custom_operation_no": int(operation_no),
            "custom_total_operation": int(total_operation)
        }
    )

    if work_order.transfer_material_against == "Job Card" and not work_order.skip_transfer:
        doc.get_required_items()

    if auto_create:
        doc.flags.ignore_mandatory = True
        if enable_capacity_planning:
            doc.schedule_time_logs(row)

        doc.insert()
        frappe.msgprint(_("Job card {0} created").format(get_link_to_form("Job Card", doc.name)), alert=True)

    if enable_capacity_planning:
        # automatically added scheduling rows shouldn't change status to WIP
        doc.db_set("status", "Open")

    return doc

def count_distinct_runcard_no(data):
    # Use a set to store distinct custom_runcard_no values, ignoring None
    distinct_runcard_no = {item['custom_runcard_no'] for item in data if item['custom_runcard_no'] is not None}
    return len(distinct_runcard_no)

def ensure_json(data):
    if isinstance(data, str):
        return json.loads(data)
    return data
