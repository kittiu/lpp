# Import required libraries
import frappe
from frappe import _
from erpnext.stock.report.stock_balance.stock_balance import execute as stock_balance_execute

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    return [
        {"label": _("รหัสสินค้า (Product Code)"), "fieldname": "item_code", "fieldtype": "Data", "width": 200},
        {"label": _("ชื่อสินค้า (Product Name)"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("หน่วยนับ (Unit)"), "fieldname": "stock_uom", "fieldtype": "Data", "width": 150},
        {"label": _("ยอดคงเหลือ (Balance)"), "fieldname": "bal_qty", "fieldtype": "Float", "width": 150},
        {"label": _("มูลค่าต่อหน่วย (Unit Price)"), "fieldname": "val_rate", "fieldtype": "Currency", "width": 150},
        {"label": _("รวมมูลค่า (Total)"), "fieldname": "bal_val", "fieldtype": "Currency", "width": 150},
    ]

def get_data(filters):
	data = []
	stock_balance = stock_balance_execute(filters)
	if stock_balance:
		stock_balance_data = stock_balance[1]
		data = stock_balance_data
	return data