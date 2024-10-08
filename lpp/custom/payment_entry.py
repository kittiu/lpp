import frappe # type: ignore
import json
from ast import literal_eval

@frappe.whitelist()
def make_withholding_tax_cert(filters, doc):
	wht = get_withholding_tax(filters, doc)
	filters = literal_eval(filters)
	pay = json.loads(doc)
	cert = frappe.new_doc("Withholding Tax Cert")
	cert.supplier = pay.get("party_type") == "Supplier" and pay.get("party") or ""
	if cert.supplier != "":
		supplier = frappe.get_doc("Supplier", cert.supplier)
		cert.supplier_name = supplier and supplier.supplier_name or ""
		# ดึง supplier_address จาก Doctype Address โดย filter ด้วย supplier_name
		address_data = frappe.db.get_value("Address", {"address_title": supplier.supplier_name}, "name")
		cert.supplier_address = address_data
	cert.voucher_type = "Payment Entry"
	cert.voucher_no = pay.get("name")
	cert.company_address = filters.get("company_address")
	cert.income_tax_form = filters.get("income_tax_form")
	cert.date = filters.get("date")
	cert.append(
		"withholding_tax_items",
		{
			"tax_base": wht["base"],
			"tax_rate": wht["rate"],
			"tax_amount": wht["amount"],
		},
	)
	return cert

@frappe.whitelist()
def get_withholding_tax(filters, doc):
	filters = literal_eval(filters)
	pay = json.loads(doc)
	wht = frappe.get_doc("Withholding Tax Type", filters["wht_type"])
	company = frappe.get_doc("Company", pay["company"])
	base_amount = 0

	for ref in pay.get("references"):
		if ref.get("reference_doctype") not in [
				"Purchase Invoice",
				"Expense Claim",
				"Journal Entry",
				"Purchase Billing"
			]:
			return
		if not ref.get("allocated_amount") or not ref.get("total_amount"):
			continue

		# Find gl entry of ref doc that has undue amount
		gl_entries = frappe.db.get_all(
			"GL Entry",
			filters={
				"voucher_type": ref["reference_doctype"],
				"voucher_no": ref["reference_name"],
			},
			fields=[
				"name",
				"account",
				"debit",
				"credit",
			],
		)
		for gl in gl_entries:
			credit = gl["credit"]
			debit = gl["debit"]
			alloc_percent = ref["allocated_amount"] / ref["total_amount"]
			report_type = frappe.get_cached_value("Account", gl["account"], "report_type")
			if report_type == "Profit and Loss":
				base_amount += alloc_percent * (credit - debit)
	return {
		"account": wht.account,
		"cost_center": company.cost_center,
		"base": base_amount,
		"rate": wht.percent,
		"amount": wht.percent / 100 * base_amount
	}