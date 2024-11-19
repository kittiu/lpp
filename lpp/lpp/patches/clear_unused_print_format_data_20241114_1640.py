import frappe

def execute():
    # ระบุชื่อของ Print Format ที่ต้องการลบในรูปแบบของรายการ
    print_format_names = ['CNS Original','CNS Size A5','Qrcode Barcode']

    for print_format_name in print_format_names:
        try:
            # ค้นหาและลบ Print Format
            print_format = frappe.get_doc("Print Format", print_format_name)
            print_format.delete()
            frappe.db.commit()
            frappe.log("Successfully deleted Print Format: {}".format(print_format_name))
        except frappe.DoesNotExistError:
            frappe.log("Print Format '{}' does not exist.".format(print_format_name))
        except Exception as e:
            frappe.log("An error occurred while deleting Print Format '{}': {}".format(print_format_name, str(e)))

