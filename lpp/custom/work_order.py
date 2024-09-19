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
    # Check if data is a string (which it seems to be based on the error)
    if isinstance(data, str):
        # Parse the string as JSON
        data = json.loads(data)
        
    count_amount = data['custom_total_run_cards']
    count_jobcard = frappe.db.count('Job Card', {'work_order': data['name']})
    count_operation = frappe.db.count('Work Order Operation', {'parent': data['name']})
    result = count_amount - (count_jobcard / count_operation)

    return result


@frappe.whitelist()
def make_job_card(work_order, operations):
    if isinstance(operations, str):
        operations = json.loads(operations)

    if isinstance(work_order, str):
        work_order = json.loads(work_order)
    
    if work_order['custom_jobcard_remaining']:

        amount = work_order['custom_total_run_cards']
        remaining = work_order['custom_jobcard_remaining']

        work_order = frappe.get_doc("Work Order", work_order['name'])
    
        for row in operations:
            row = frappe._dict(row)
            runcard_no = f"{(amount - remaining) + 1}/{amount}"
            validate_operation_data(row)
            qty = row.get("qty")
            while qty > 0:
                qty = split_qty_based_on_batch_size(work_order, row, qty)
                if row.job_card_qty > 0:
                    create_job_card(work_order, row, runcard_no, auto_create=True)
    else:
        msgprint(_('จำนวน Runcard เกินกว่าที่กำหนด'))
        

def create_job_card(work_order, row, runcard_no, enable_capacity_planning=False, auto_create=False):
    doc = frappe.new_doc("Job Card")
    print('runcard_no', runcard_no)
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
            "custom_runcard_no": runcard_no
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