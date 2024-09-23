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

def get_next_sequence(last_number, date_part):
    """
    Helper function to calculate the next sequence number.
    """
    if last_number and last_number[0][0]:
        last_seq_num = int(re.search(r'\d{3}', last_number[0][0]).group())
        return last_seq_num + 1
    else:
        return 1


class CustomBatch(Batch):
    def autoname(self):
        """Generate random ID for batch if not specified"""
        # Get current year and month in YY.MM format
        date_part = datetime.datetime.now().strftime("%y.%m")
        # Check if custom_rescreen is True or False
        rescreen_suffix = ".-R" if self.custom_rescreen else ""
        # Handle naming for "Buying"
        if self.custom_lot_type == "Buying":
            # Separate sequence for Buying
            params_name = f"""name like "{date_part}%" """
            last_number = frappe.db.sql("""SELECT MAX(name) FROM `tabBatch` WHERE custom_lot_type="Buying" and """+params_name)
            
            next_number = get_next_sequence(last_number, date_part)
            # Set name as YY.MM.### or YY.MM.###-R
            self.name = f"{date_part}.{next_number:03d}{rescreen_suffix}"
        
        # Handle naming for "Selling"
        elif self.custom_lot_type == "Selling":
            # Get the 'custom_in_short' field from the linked item group (item.custom_in_short)
            custom_item_group_2 = frappe.db.get_value("Item", self.item, "custom_item_group_2")
            item2_group_in_short = frappe.db.get_value("Item Group", custom_item_group_2, "custom_in_short")
            # Separate sequence for 
            params_name = f"""name like "{date_part}%" """
            last_number = frappe.db.sql("""SELECT MAX(name) FROM `tabBatch` WHERE custom_lot_type="Selling" and """+params_name)
            next_number = get_next_sequence(last_number, date_part)
            # Set name as YY.MM.[item_in_short].### or YY.MM.[item_in_short].###-R
            self.name = f"{date_part}.{item2_group_in_short}.{next_number:03d}{rescreen_suffix}"

