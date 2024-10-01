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

def get_next_sequence(last_lot_no):
    """
    Helper function to calculate the next sequence number from the last batch name.
    Extracts the sequence number from positions 5 to 7.
    """
    print("")
    if last_lot_no and len(last_lot_no) >= 7:
        last_seq_num = int(last_lot_no[4:7])
        return last_seq_num + 1
    return 1


class CustomBatch(Batch):
    def autoname(self):
        """Generate the batch name based on lot no."""
        if not self.name:
            self.name =  self.batch_id

    def get_last_lot_no(self, filters):
        """Retrieve the last batch name based on filters."""
        last_batch = frappe.get_list("Batch", filters=filters, fields=["batch_id"], order_by="batch_id desc", limit=1)
        return last_batch[0].batch_id if last_batch else None

    @frappe.whitelist()
    def gen_lot_no(self): 
        """Generate a new Lot No. for the Batch."""
        # Get the last Lot No. for the Batch
        # Get current year and month in YY.MM format
        date_part = datetime.datetime.now().strftime("%y%m")
        # Set rescreen suffix if applicable
        rescreen_suffix = "-R" if self.custom_rescreen else ""
        
        # Prepare the filter for sequence query
        filters = {
            "batch_id": ["like", f"{date_part}%"],
            "custom_lot_type": self.custom_lot_type
        }

        # Determine the batch type and set the name
        if self.custom_lot_type == "Buying":
            # Separate sequence for Buying
            last_lot_no = self.get_last_lot_no(filters)
            next_number = get_next_sequence(last_lot_no)
            # Set name as YY.MM.### or YY.MM.###-R
            next_lot_no = f"{date_part}{next_number:03d}/"
            return  next_lot_no

        elif self.custom_lot_type == "Selling":
            # Get the 'custom_in_short' field from the linked item group
            custom_item_group_2 = frappe.db.get_value("Item", self.item, "custom_item_group_2")
            item2_group_in_short = frappe.db.get_value("Item Group", custom_item_group_2, "custom_in_short")
            if item2_group_in_short is  None:
                item2_group_in_short = ""
            # Separate sequence for Selling
            last_lot_no = self.get_last_lot_no(filters)
            
            next_number = get_next_sequence(last_lot_no)
            # Set name as YYMM###/[item_in_short] or YYMM###/[item_in_short]-R
            next_lot_no = f"{date_part}{next_number:03d}/{item2_group_in_short}{rescreen_suffix}"
            return next_lot_no


        

