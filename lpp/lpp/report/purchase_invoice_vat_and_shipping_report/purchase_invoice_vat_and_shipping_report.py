import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	
	# Format the VAT Code after fetching data
	for row in data:
		row["vat_code"] = format_vat_code(row["vat_code"])  # Convert to VatX% format
	
	return columns, data

def get_columns():
	return [
		{"label": "VAT Code", "fieldname": "vat_code", "fieldtype": "Data", "width": 100},
		{"label": "Invoice No./Tax Invoice No.", "fieldname": "invoice_no", "fieldtype": "Data", "width": 200},
		{"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 120},
		{"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 150},
		{"label": "Receiving Quantity", "fieldname": "rcvg_qty", "fieldtype": "Float", "width": 120},
		{"label": "Conversion Factor", "fieldname": "conversion_factor", "fieldtype": "Float", "width": 120},
		{"label": "Receiving Amount", "fieldname": "rcvg_amt", "fieldtype": "Currency", "width": 120},
		{"label": "Tax Amount", "fieldname": "tax_amount", "fieldtype": "Currency", "width": 120},
		{"label": "Invoice Date", "fieldname": "invoice_date", "fieldtype": "Date", "width": 100},
		{"label": "ETD Date", "fieldname": "due_date", "fieldtype": "Date", "width": 100},
		{"label": "Remark", "fieldname": "custom_remark", "fieldtype": "Text", "width": 150}
	]

def get_data(filters):
	# Construct filter conditions dynamically
	conditions = ""
	if filters.get("from_date"):
		conditions += " AND pi.posting_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND pi.posting_date <= %(to_date)s"
	if filters.get("invoice_no"):
		conditions += " AND pi.name = %(invoice_no)s"
	if filters.get("item_code"):
		conditions += " AND pii.item_code = %(item_code)s"
	if filters.get("end_date"):
		conditions += " AND pi.due_date <= %(end_date)s"  # Add condition for end date
	
	query = """
	SELECT
		IFNULL(ptc.rate, 0) AS vat_code,
		pii.custom_po_no AS po,
		pi.name AS invoice_no,
		pii.item_code,
		pii.item_name,
		pii.conversion_factor,
		pii.qty AS rcvg_qty,
		(pii.conversion_factor * pii.qty) AS rcvg_amt,
		pi.total_taxes_and_charges AS tax_amount,
		pi.posting_date AS invoice_date,
		pi.due_date AS due_date,
		pi.custom_remark
	FROM
		`tabPurchase Invoice` pi
	INNER JOIN
		`tabPurchase Invoice Item` pii ON pii.parent = pi.name
	LEFT JOIN
		`tabPurchase Taxes and Charges` ptc ON ptc.parent = pi.name
	WHERE
		pi.docstatus = 1
		{conditions}
	ORDER BY
		pi.posting_date DESC
	"""

	# Execute query with conditions
	data = frappe.db.sql(query.format(conditions=conditions), filters, as_dict=True)
	return data

# Function to format VAT Code
def format_vat_code(vat_code):
	# Convert VAT rate (e.g., 0, 7) to the format VatX%
	return f"Vat{int(vat_code)}%"
