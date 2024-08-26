# import frappe

# @frappe.whitelist()
# def get_contact_details(contact):
#     contact = frappe.get_doc("Contact", contact)
#     contact.check_permission()

#     return {
#         "contact_person": contact.get("name"),
#         "contact_display": f"{contact.full_name} | {contact.mobile_no}",
#         "contact_email": contact.get("email_id"),
#         "contact_mobile": contact.get("mobile_no"),
#         "contact_phone": contact.get("phone"),
#         "contact_designation": contact.get("designation"),
#         "contact_department": contact.get("department"),
#     }
