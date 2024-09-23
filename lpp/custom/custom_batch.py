import frappe
from erpnext.stock.doctype.batch.batch import Batch
from frappe.utils import cint
import datetime
import re

def get_name_from_hash():
	"""
	Get a name for a Batch by generating a unique hash.
	:return: The hash that was generated.
	"""
	temp = None
	while not temp:
		temp = frappe.generate_hash()[:7].upper()
		if frappe.db.exists("Batch", temp):
			temp = None

	return temp

def batch_uses_naming_series():
	"""
	Verify if the Batch is to be named using a naming series
	:return: bool
	"""
	use_naming_series = cint(frappe.db.get_single_value("Stock Settings", "use_naming_series"))
	return bool(use_naming_series)

def get_next_sequence(last_name):
    """
    Helper function to calculate the next sequence number from the last batch name.
    """
    if last_name:
        last_seq_num = int(re.search(r'\d{3}', last_name).group())
        return last_seq_num + 1
    return 1


class CustomBatch(Batch):
    def autoname(self):
        """Generate the batch name based on custom logic for Buying or Selling."""
        # Get current year and month in YY.MM format
        date_part = datetime.datetime.now().strftime("%y.%m")
        # Set rescreen suffix if applicable
        rescreen_suffix = "-R" if self.custom_rescreen else ""
        
        # Prepare the filter for sequence query
        filters = {
            "name": ["like", f"{date_part}%"],
            "custom_lot_type": self.custom_lot_type
        }

        # Determine the batch type and set the name
        if self.custom_lot_type == "Buying":
            # Separate sequence for Buying
            last_name = self.get_last_batch_name(filters)
            next_number = get_next_sequence(last_name)
            # Set name as YY.MM.### or YY.MM.###-R
            self.name = f"{date_part}.{next_number:03d}{rescreen_suffix}"

        elif self.custom_lot_type == "Selling":
            # Get the 'custom_in_short' field from the linked item group
            custom_item_group_2 = frappe.db.get_value("Item", self.item, "custom_item_group_2")
            item2_group_in_short = frappe.db.get_value("Item Group", custom_item_group_2, "custom_in_short")
            
            # Separate sequence for Selling
            last_name = self.get_last_batch_name(filters)
            next_number = get_next_sequence(last_name)
            # Set name as YY.MM.[item_in_short].### or YY.MM.[item_in_short].###-R
            self.name = f"{date_part}.{item2_group_in_short}.{next_number:03d}{rescreen_suffix}"

    def get_last_batch_name(self, filters):
        """Retrieve the last batch name based on filters."""
        last_batch = frappe.get_list("Batch", filters=filters, fields=["name"], order_by="name desc", limit=1)
        return last_batch[0].name if last_batch else None

