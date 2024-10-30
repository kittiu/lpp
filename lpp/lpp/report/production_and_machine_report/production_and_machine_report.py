# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _, scrub
from datetime import date


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
   
    return columns, data

def get_columns():
    columns = [
        {
			"label": _("Workstation"),
			"fieldname": "workstation",
			"fieldtype": "Data",
			"width": 400,
            "align": "left"
		},
        {
			"label": _("QTY"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 160,
		},
        {
			"label": _("%"),
			"fieldname": "percent",
			"fieldtype": "Float",
			"width": 160,
		}
	]
    return columns

def get_data(filters):
    report_data = []
    get_workstation = None
    from_date = None
    to_date = None
    
    
    # Check if 'workstation' exists in filters and has at least one value
    if filters.get("workstation") and len(filters.get("workstation")) > 0:
        get_workstation = filters.get("workstation")
    else:
        query_work = frappe.db.sql(
                f"""SELECT tw.name 
                    FROM `tabWorkstation` tw 
                    INNER JOIN `tabWorkstation Type` twt ON tw.workstation_type = twt.name 
                    WHERE twt.name = '{filters.get("workstation_type")}'
                """,
                as_dict=True,
            )
        
        # get Workstation by Workstation Type
        get_workstation = []
        for w in query_work:
            get_workstation.append(w.get('name'))
        
    if get_workstation:
        for idx, ws in enumerate(get_workstation, start=1):
            custom_input = 0

            if idx > 1:
                report_data.append({
                    "workstation": "",
                    "qty": None,
                    "percent": None
                })

            if filters:
                from_date = filters['from_date']
                to_date = filters['to_date']
            else: 
                # Get the current date
                from_date = date.today()
                to_date = date.today()
                
            # Query production data (input, output, hours, maximum capacity)
            query_in_out = frappe.db.sql(
                f"""SELECT SUM(tjc.custom_input_production) AS custom_input, 
                           SUM(tjc.custom_output_production) AS custom_output,
                           SUM(tjc.custom_total_hours_production) AS total_hours,
                           SUM(tw.custom_maximum_capacity_work_hour_) AS maximum_capacity
                    FROM `tabWorkstation Type` twt 
                    INNER JOIN `tabWorkstation` tw ON twt.name = tw.workstation_type 
                    INNER JOIN `tabJob Card` tjc ON tw.name = tjc.workstation 
                    WHERE tw.name = '{ws}'
                    AND tjc.posting_date BETWEEN '{from_date}' AND '{to_date}'
                """,
                as_dict=True,
            )
            
            # Loop through the query results for production data
            for io in query_in_out:
                custom_input = io.get('custom_input', 0)
                custom_output = io.get('custom_output', 0)
                total_hours = io.get('total_hours', 0)
                maximum_capacity = io.get('maximum_capacity', 0)

                # IN, OUT, and Machine summary
                report_data.append({
                    "workstation": ws,
                    "qty": None,
                    "percent": None
                })
                report_data.append({
                    "workstation": "IN",
                    "qty": custom_input,
                    "percent": None
                })
                report_data.append({
                    "workstation": "OUT",
                    "qty": custom_output,
                    "percent": (custom_output / custom_input) * 100 if custom_input else 0
                })
                
            # Query defect data
            query_defect = frappe.db.sql(
                f"""SELECT tjcsi.custom_defect, 
                           SUM(tjcsi.stock_qty) AS sum_qty
                    FROM `tabJob Card` tjc 
                    INNER JOIN `tabJob Card Scrap Item` tjcsi ON tjc.name = tjcsi.parent 
                    WHERE tjc.workstation = '{ws}'
                    AND tjc.posting_date BETWEEN '{from_date}' AND '{to_date}'
                    GROUP BY tjcsi.custom_defect
                """,
                as_dict=True,
            )
                
            # Loop to show defect and quantity
            report_data.append({
				"workstation": "DEFECT",
				"qty": None,
				"percent": None
			})
            sum_qty = 0
            
            for df in query_defect:
                sum_qty += df.get('sum_qty', 0)
                report_data.append({
                    "workstation": df.get('custom_defect'),
                    "qty": df.get('sum_qty', 0),
                    "percent": None
                })

            # Total Defect  
            custom_input = 1 if custom_input is None else custom_input
            custom_input = custom_input if custom_input != 0 else 1
            report_data.append({
				"workstation": "TOTAL DEFECT",
				"qty": sum_qty,
				"percent": (sum_qty/custom_input)*100
			})
                
            # Loop through the query results again for machine details
            for io in query_in_out:
                custom_input = io.get('custom_input', 0)
                custom_output = io.get('custom_output', 0)
                total_hours = io.get('total_hours', 0)
                maximum_capacity = io.get('maximum_capacity', 0)

                # MACHINE details
                report_data.append({
                    "workstation": "",
                    "qty": None,
                    "percent": None
                })
                report_data.append({
                    "workstation": f"MACHINE : {ws}",
                    "qty": None,
                    "percent": None
                })
                report_data.append({
                    "workstation": "MAXIMUM CAPACITY(Hrs.)",
                    "qty": maximum_capacity,
                    "percent": None
                })
                report_data.append({
                    "workstation": "WORKING HOURS(Hrs.)",
                    "qty": total_hours,
                    "percent": None
                })
                report_data.append({
                    "workstation": "UPH(pcs)",
                    "qty": (custom_input / total_hours) if total_hours else 0,
                    "percent": None
                })

    return report_data