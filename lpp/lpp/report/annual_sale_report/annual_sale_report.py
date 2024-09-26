import frappe
from .quarter import quarter  # Optimized import for the current directory
from .monthly import monthly

def execute(filters=None):
    # ตรวจสอบว่า filters ไม่ใช่ค่า None
    if not filters or "type" not in filters:
        frappe.log_error(message="Filter type is missing.", title="Filter Error")
        return [], []

    # ตรวจสอบค่าใน filters ว่าจะเรียกใช้ quarter หรือ monthly
    try:
        if filters["type"] == "Quarter":
            # เรียกใช้ quarter function
            columns, data = quarter(filters)
        elif filters["type"] == "Monthly":
            # เรียกใช้ monthly function
            columns, data = monthly(filters)
        else:
            # ถ้า filters["type"] ไม่ตรงกับเงื่อนไข ให้ส่งข้อความ error กลับ
            frappe.log_error(message=f"Unknown report type: {filters['type']}", title="Invalid Filter Type")
            return [], []
        
        return columns, data
    except Exception as e:
        # Handle potential errors and provide meaningful feedback
        frappe.log_error(message=str(e), title="Report Generation Error")
        return [], []
