import frappe
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"label": "Supplyer Code",
			"fieldname": "customer",
			"fieldtype": "Data",
			"width": 130,
			"align": "left"
		},
		{
			"label": "Supplyer Name",
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 200,
			"align": "left"
		},
		{
			"label": "Delivery Date",
			"fieldname": "due_date",
			"fieldtype": "Date",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Vendor Invoice Number for Delivery",
			"fieldname": "custom_supplier_purchase_order",
			"fieldtype": "Data",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Purchasing Document Number",
			"fieldname": "purchase_order_number",
			"fieldtype": "Data",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Inco terms",
			"fieldname": "",
			"fieldtype": "Data",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Material Number",
			"fieldname": "custom_material",
			"fieldtype": "Data",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Actual quantity delivered (in sale units)",
			"fieldname": "actual_qty",
			"fieldtype": "Float",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Purchase Order Unit of Measure",
			"fieldname": "uom",
			"fieldtype": "Data",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Document Currency",
			"fieldname": "currency",
			"fieldtype": "Data",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Unit price",
			"fieldname": "rate",
			"fieldtype": "Currency",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Exchange rate",
			"fieldname": "conversion_rate",
			"fieldtype": "Float",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Document Currency Amount",
			"fieldname": "document_cur_amount",
			"fieldtype": "Currency",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Unit price (Baht)",
			"fieldname": "rate_baht",
			"fieldtype": "Currency",
			"width": 140,
			"align": "left"
		},
		{
			"label": "Local Currency Amount",
			"fieldname": "local_cur_amount",
			"fieldtype": "Currency",
			"width": 140,
			"align": "left"
		}
	]

def get_data(filters):
	conditions = "1=1"

	if filters.get("customer_name"):
		conditions += " AND si.customer = %(customer_name)s"
	# Filter by date range
	if filters.get("from_date"):
		conditions += " AND si.due_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND si.due_date <= %(to_date)s"	

	# ดึงข้อมูลจาก Sales Invoice
	invoices = frappe.db.sql("""
		SELECT
			si.customer,
			si.customer_name,
			si.due_date,
			si.custom_supplier_purchase_order,
			sii.qty,
			si.currency,
			sii.rate,
			si.conversion_rate,
			sii.uom,
			si.name,
			it.item_code,
			it.item_name,
			it.custom_material
		FROM
			`tabSales Invoice` si
		INNER JOIN 
			`tabSales Invoice Item` sii ON si.name = sii.parent
		LEFT JOIN 
			`tabItem` it ON sii.item_code = it.name
		WHERE
			{conditions}
	""".format(conditions=conditions), filters, as_dict=True)

	data = []

	for inv in invoices:
		document_cur_amount = flt(inv.qty) * flt(inv.rate) * flt(inv.conversion_rate)
		local_cur_amount = flt(inv.qty) * flt(inv.rate)

		row = {
			"customer": inv.customer,
			"customer_name": inv.customer_name,
			"due_date": inv.due_date,
			"custom_supplier_purchase_order": inv.custom_supplier_purchase_order,
			"purchase_order_number": "",
			"inco_terms": "",
			"custom_material": inv.custom_material,
			"actual_qty": inv.qty,
			"uom": inv.uom,
			"currency": inv.currency,
			"rate": inv.rate,
			"conversion_rate": inv.conversion_rate,
			"document_cur_amount": document_cur_amount,
			"rate_baht": inv.rate,
			"local_cur_amount": local_cur_amount
		}

		data.append(row)

	return data