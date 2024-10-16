import frappe
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt , get_returned_qty_map , get_invoiced_qty_map
from frappe.utils import flt
from erpnext.controllers.accounts_controller import merge_taxes
from erpnext.accounts.party import get_payment_terms_template
from frappe.model.mapper import get_mapped_doc

class CustomPurchaseReceipt(PurchaseReceipt):
	def on_cancel(self):

			self.check_on_hold_or_closed_status()
			# Check if Purchase Invoice has been submitted against current Purchase Order
			submitted = frappe.db.sql(
				"""select t1.name
				from `tabPurchase Invoice` t1,`tabPurchase Invoice Item` t2
				where t1.name = t2.parent and t2.purchase_receipt = %s and t1.docstatus = 1""",
				self.name,
			)
			if submitted:
				frappe.throw(_("Purchase Invoice {0} is already submitted").format(submitted[0][0]))

			self.update_prevdoc_status()
			self.update_billing_status()

			# Updating stock ledger should always be called after updating prevdoc status,
			# because updating ordered qty in bin depends upon updated ordered qty in PO
			self.update_stock_ledger()
			self.make_gl_entries_on_cancel()
			self.repost_future_sle_and_gle()
			self.ignore_linked_doctypes = (
				"GL Entry",
				"Stock Ledger Entry",
				"Repost Item Valuation",
				"Serial and Batch Bundle",
			)
			# self.delete_auto_created_batches()
			self.set_consumed_qty_in_subcontract_order()
   
@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None, args=None):
	print("+"*100)
	doc = frappe.get_doc("Purchase Receipt", source_name)
	returned_qty_map = get_returned_qty_map(source_name)
	invoiced_qty_map = get_invoiced_qty_map(source_name)

	def set_missing_values(source, target):
		if len(target.get("items")) == 0:
			frappe.throw(_("All items have already been Invoiced/Returned"))

		doc = frappe.get_doc(target)
		doc.payment_terms_template = get_payment_terms_template(source.supplier, "Supplier", source.company)
		doc.run_method("onload")
		doc.run_method("set_missing_values")

		if args and args.get("merge_taxes"):
			merge_taxes(source.get("taxes") or [], doc)

		doc.run_method("calculate_taxes_and_totals")
		doc.set_payment_schedule()

	def update_item(source_doc, target_doc, source_parent):
		target_doc.qty, returned_qty = get_pending_qty(source_doc)
		if frappe.db.get_single_value("Buying Settings", "bill_for_rejected_quantity_in_purchase_invoice"):
			target_doc.rejected_qty = 0
		target_doc.stock_qty = flt(target_doc.qty) * flt(
			target_doc.conversion_factor, target_doc.precision("conversion_factor")
		)
		returned_qty_map[source_doc.name] = returned_qty

	def get_pending_qty(item_row):
		qty = item_row.qty
		if frappe.db.get_single_value("Buying Settings", "bill_for_rejected_quantity_in_purchase_invoice"):
			qty = item_row.received_qty

		pending_qty = qty - invoiced_qty_map.get(item_row.name, 0)

		if frappe.db.get_single_value("Buying Settings", "bill_for_rejected_quantity_in_purchase_invoice"):
			return pending_qty, 0

		returned_qty = flt(returned_qty_map.get(item_row.name, 0))
		if returned_qty:
			if returned_qty >= pending_qty:
				pending_qty = 0
				returned_qty -= pending_qty
			else:
				pending_qty -= returned_qty
				returned_qty = 0

		return pending_qty, returned_qty

	doclist = get_mapped_doc(
		"Purchase Receipt",
		source_name,
		{
			"Purchase Receipt": {
				"doctype": "Purchase Invoice",
				"field_map": {
					"supplier_warehouse": "supplier_warehouse",
					"is_return": "is_return",
					"bill_date": "bill_date",
					"supplier_delivery_note" :  "custom_supplier_delivery_note",
					"custom_supplier__invoice" :  "custom_supplier_invoice",
				},
				"validation": {
					"docstatus": ["=", 1],
				},
			},
			"Purchase Receipt Item": {
				"doctype": "Purchase Invoice Item",
				"field_map": {
					"name": "pr_detail",
					"parent": "purchase_receipt",
					"qty": "received_qty",
					"purchase_order_item": "po_detail",
					"purchase_order": "purchase_order",
					"is_fixed_asset": "is_fixed_asset",
					"asset_location": "asset_location",
					"asset_category": "asset_category",
					"wip_composite_asset": "wip_composite_asset",
				},
				"postprocess": update_item,
				"filter": lambda d: get_pending_qty(d)[0] <= 0
				if not doc.get("is_return")
				else get_pending_qty(d)[0] > 0,
			},
			"Purchase Taxes and Charges": {
				"doctype": "Purchase Taxes and Charges",
				"reset_value": not (args and args.get("merge_taxes")),
				"ignore": args.get("merge_taxes") if args else 0,
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist