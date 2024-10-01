import frappe # type: ignore
import json
from frappe import _, msgprint
from frappe.utils import (
    get_link_to_form,
    nowdate,
)
from erpnext.manufacturing.doctype.work_order.work_order import validate_operation_data, split_qty_based_on_batch_size

@frappe.whitelist()
def get_jobcard_remaining(data): 
    data = ensure_json(data)  # Ensure data is parsed once

    job_cards = frappe.db.get_all('Job Card', 
        filters={'work_order': data['name']}, 
        fields=['custom_runcard_no',],
        group_by='custom_runcard_no'
    )

    count_amount = data['custom_total_run_cards']
    count_jobcard = count_distinct_runcard_no(job_cards)
    result = count_amount - count_jobcard

    return result


@frappe.whitelist()
def make_job_card(work_order, operations):
    work_order = ensure_json(work_order)
    operations = ensure_json(operations)
    
    if work_order['custom_jobcard_remaining'] and work_order['custom_total_run_cards']:

        amount = work_order['custom_total_run_cards']

        work_order = frappe.get_doc("Work Order", work_order['name'])

        custom_quantity__run_card = int(work_order.custom_quantity__run_card)

        job_card_creation_list = []  # ลิสต์เก็บข้อมูลที่จะใช้สร้าง job card
        validation_failed = False    # Flag เพื่อบอกว่ามี validation ล้มเหลวหรือไม่

        for row in operations:
            row = frappe._dict(row)
            validate_operation_data(row)
            qty = row.get("qty")

            if not qty:  # Skip if qty is not valid
                continue

            job_cards = frappe.db.get_all('Job Card', 
                filters={
                    'work_order': work_order.name, 
                    'operation': row.operation,
                },
                fields=['custom_runcard_no', 'SUM(for_quantity) as for_quantity'],
                group_by='custom_runcard_no'
            )

            max_runcard_no = count_distinct_runcard_no(job_cards)
            if max_runcard_no == 0:
                max_runcard_no = 1
            runcard_no = f"{max_runcard_no}/{amount}"

            job_card_dict = {item['custom_runcard_no']: item['for_quantity'] for item in job_cards}
            total = job_card_dict.get(runcard_no, 0)  # Defaults to 0 if runcard_no not found

            # Validate conditions for run card
            if custom_quantity__run_card == total and custom_quantity__run_card >= qty:
                # Prepare the next run card for creation
                runcard_no = f"{(max_runcard_no) + 1}/{amount}"
                sequence = 1
                # Append the data to the creation list
                job_card_creation_list.append((work_order, row, qty, runcard_no, sequence))

            elif custom_quantity__run_card >= (total + qty):
                sequence = len(job_cards) + 1
                # Append the data to the creation list
                job_card_creation_list.append((work_order, row, qty, runcard_no, sequence))

            else:
                # Validation failed, stop the process and show a message
                msgprint(_(f"จำนวนสั่งผลิตมากเกินกว่าจำนวนต่อ Runcard ({row.operation})"))
                validation_failed = True  # Mark validation as failed
                break  # Exit the loop if validation fails

        # Check if validation passed for all rows
        if not validation_failed and job_card_creation_list:
            # Process job card creation after all validation is complete
            for job_card_data in job_card_creation_list:
                process_job_card_creation(*job_card_data)

    else:
        msgprint(_('จำนวน Runcard เกินกว่าที่กำหนด'))

def process_job_card_creation(work_order, row, qty, runcard_no, sequence=1):
    while qty > 0:
        qty = split_qty_based_on_batch_size(work_order, row, qty)
        if row.job_card_qty > 0:
            create_job_card(work_order, row, runcard_no, sequence, auto_create=True)


def create_job_card(work_order, row, runcard_no, sequence, enable_capacity_planning=False, auto_create=False):
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
            "custom_sequence": sequence
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