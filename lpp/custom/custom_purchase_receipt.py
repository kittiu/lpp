import frappe
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt

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