import frappe
from erpnext.manufacturing.doctype.bom.bom import BOM
from frappe import _

class CustomBOM(BOM):

	def autoname(self):

		search_key = f"{self.doctype}-{self.item}%"
		existing_boms = frappe.get_all(
			"BOM", filters={"name": ("like", search_key), "amended_from": ["is", "not set"]}, pluck="name"
		)

		if existing_boms:
			index = self.get_next_version_index(existing_boms)
		else:
			index = 1

		prefix = self.doctype
		suffix = "%.2i" % index  # convert index to string (1 -> "01")
		bom_name = f"{prefix}-{self.item}-{suffix}"

		if len(bom_name) <= 140:
			name = bom_name
		else:
			# since max characters for name is 140, remove enough characters from the
			# item name to fit the prefix, suffix and the separators
			truncated_length = 140 - (len(prefix) + len(suffix) + 2)
			truncated_item_name = self.item[:truncated_length]
			# if a partial word is found after truncate, remove the extra characters
			truncated_item_name = truncated_item_name.rsplit(" ", 1)[0]
			name = f"{prefix}-{truncated_item_name}-{suffix}"

		if frappe.db.exists("BOM", name):
			conflicting_bom = frappe.get_doc("BOM", name)

			if conflicting_bom.item != self.item:
				msg = _("A BOM with name {0} already exists for item {1}.").format(
					frappe.bold(name), frappe.bold(conflicting_bom.item)
				)

				frappe.throw(
					_("{0}{1} Did you rename the item? Please contact Administrator / Tech support").format(
						msg, "<br>"
					)
				)

		self.name = name