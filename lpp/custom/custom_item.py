from erpnext.stock.doctype.item.item import Item
from frappe.model.naming import make_autoname
import frappe
import json
from collections import OrderedDict, defaultdict
from frappe import qb, scrub
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.query_builder import Criterion, CustomFunction
from frappe.query_builder.functions import Concat, Locate, Sum
from frappe.utils import nowdate


class CustomItem(Item):
    def autoname(self):
        # You can call the original autoname method of Item if needed
        if self.custom_abbreviation:
            # Use dot (.) to separate the prefix from the numeric part
            self.name = make_autoname(f"{self.custom_abbreviation}-.#####")
        else:
            frappe.throw("Custom Abbreviation is required for auto-naming.")

    # Add or override any other methods specific to CustomItem
    def validate(self):
        # Call the original validate method of Item
        super().validate()
        self.meta.get_field("item_code").reqd = 0
        # Custom validation logic if needed
        # if not self.custom_abbreviation:
        #     frappe.throw("Custom Abbreviation is mandatory for this item.")


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_items_based_on_party_and_groups(doctype, txt, searchfield, start, page_len, filters):
    party_name = filters.get("party_name")  # รับค่า party_name จาก filters
    # SQL Query
    query = """
    SELECT name, item_code, description
    FROM `tabItem`
    WHERE docstatus < 2
    AND ({key} LIKE %(txt)s
        OR name LIKE %(txt)s
        OR description LIKE %(txt)s)
    AND (
        EXISTS (
            SELECT 1
            FROM `tabItem Customer Detail` ci
            WHERE ci.parent = `tabItem`.name
            AND ci.customer_name = %(party_name)s
        )
        OR (
            NOT EXISTS (
                SELECT 1
                FROM `tabItem Customer Detail` ci
                WHERE ci.parent = `tabItem`.name
            )
            AND item_group = 'Sales Product'
            AND custom_item_group_2 = 'Other'
        )
        OR (
            NOT EXISTS (
                SELECT 1
                FROM `tabItem Customer Detail` ci
                WHERE ci.parent = `tabItem`.name
            )
            AND custom_item_group_3 = 'Mold & Tooling'
        )
    )
    {mcond}
    ORDER BY name
    LIMIT %(start)s, %(page_len)s
    """.format(**{
        'key': searchfield,
        'mcond': get_match_cond(doctype)
    })

    # Parameters
    params = {
        'txt': "%{}%".format(txt),
        '_txt': txt.replace("%", ""),
        'start': start,
        'page_len': page_len,
        'party_name': party_name
    }
    
    # Execute Query
    return frappe.db.sql(query, params)
