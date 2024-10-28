import frappe
from .tray_and_reel import tray_and_reel

def execute(filters=None):
    if not filters or "type" not in filters:
        frappe.log_error(message="Filter type is missing.", title="Filter Error")
        return [], []
    
    try:
        if filters["type"] == "Tray & Reel":
            columns, data = tray_and_reel(filters)
        else:
            # ถ้า filters["type"] ไม่ตรงกับเงื่อนไข ให้ส่งข้อความ error กลับ
            frappe.log_error(message=f"Unknown report type: {filters['type']}", title="Invalid Filter Type")
            return [], []
        
        return columns, data
    except Exception as e:
        # Handle potential errors and provide meaningful feedback
        frappe.log_error(message=str(e), title="Report Generation Error")
        return [], []