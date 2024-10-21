frappe.ui.form.on("Purchase Receipt", {
	refresh(frm) {
		frm.set_df_property('posting_time', 'hidden', true);

		setTimeout(() => {
			if (!frm.is_new() && frm.doc.docstatus === 0 && frappe.model.can_create("Quality Inspection")) {
				// Remove Original Button
				frm.remove_custom_button(__('Quality Inspection(s)'))
				frm.add_custom_button(__("Quality Inspection(s)"), async () => {

					frm.trigger("make_quality_inspection_new");
					
				}, __("Create"));
				frm.page.set_inner_btn_group_as_primary(__('Create'));
			}
		}, 10);
	},

	async make_quality_inspection_new  (frm) {

		let data = [];
		const fields = [
			{
				label: "Items",
				fieldtype: "Table",
				fieldname: "items",
				cannot_add_rows: true,
				in_place_edit: true,
				data: data,
				get_data: () => {
					return data;
				},
				fields: [
					{
						fieldtype: "Data",
						fieldname: "docname",
						hidden: true
					},
					{
						fieldtype: "Read Only",
						fieldname: "item_code",
						label: __("Item Code"),
						in_list_view: true
					},
					{
						fieldtype: "Read Only",
						fieldname: "item_name",
						label: __("Item Name"),
						in_list_view: true
					},
					{
						fieldtype: "Float",
						fieldname: "qty",
						label: __("Accepted Quantity"),
						in_list_view: true,
						read_only: true
					},
					{
						fieldtype: "Float",
						fieldname: "sample_size",
						label: __("Sample Size"),
						reqd: true,
						in_list_view: true
					},
					{
						fieldtype: "Float",
						fieldname: "custom_accepted_quantity_imqa_uom",
						label: __("Accepted Quantity (IMQA UOM)"),
						in_list_view: true
					},
					{
						fieldtype: "Data",
						fieldname: "description",
						label: __("Description"),
						hidden: true
					},
					{
						fieldtype: "Data",
						fieldname: "serial_no",
						label: __("Serial No"),
						hidden: true
					},
					{
						fieldtype: "Data",
						fieldname: "batch_no",
						label: __("Batch No"),
						hidden: true
					}
				]
			}
		];

		const dialog = new frappe.ui.Dialog({
			title: __("Select Items for Quality Inspection"),
			size: "extra-large",
			fields: fields,
			primary_action: async function () {
				const data = dialog.get_values();
				frappe.call({
					method: "erpnext.controllers.stock_controller.make_quality_inspections",
					args: {
						doctype: frm.doc.doctype,
						docname: frm.doc.name,
						items: data.items
					},
					freeze: true,
					callback: function (r) {
						if (r.message.length > 0) {

							if (r.message.length === 1) {
								frappe.set_route("Form", "Quality Inspection", r.message[0]);
							} else {
								frappe.route_options = {
									"reference_type": frm.doc.doctype,
									"reference_name": frm.doc.name
								};
								frappe.set_route("List", "Quality Inspection");
							}
						}
						dialog.hide();
					}
				});
			},
			primary_action_label: __("Create")
		});

		frm.doc.items.forEach(item => {
			if (has_inspection_required(frm, item)) {
				let dialog_items = dialog.fields_dict.items;
				dialog_items.df.data.push({
					"docname": item.name,
					"item_code": item.item_code,
					"item_name": item.item_name,
					"qty": item.qty,
					"description": item.description,
					"serial_no": item.serial_no,
					"batch_no": item.batch_no,
					"sample_size": item.sample_quantity
				});
				dialog_items.grid.refresh();
			}
		});

		data = dialog.fields_dict.items.df.data;
		const is_existing = await is_existing_quality_inspections(frm)
		
		if (!data.length || is_existing) {
			frappe.msgprint(__("All items in this document already have a linked Quality Inspection."));
		} else {
			dialog.show();
		}
	},


});

function has_inspection_required(frm, item) {
    if (frm.doc.doctype === "Stock Entry" && frm.doc.purpose == "Manufacture" ) {
        if (item.is_finished_item && !item.quality_inspection) {
            return true;
        }
    } 
	else if (!item.quality_inspection) {		
        return true;
    }
}

function is_existing_quality_inspections(frm) {
    return new Promise((resolve, reject) => {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Quality Inspection",
                filters: {'reference_name': frm.doc.name},
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    resolve(true); // Quality Inspections exist
                } else {
                    resolve(false); // No Quality Inspections found
                }
            },
            error: function(err) {
                reject(err); // Handle errors
            }
        });
    });
}


frappe.ui.form.on("Purchase Receipt Item", "rate", function (frm, cdt, cdn) {
	var item = frappe.get_doc(cdt, cdn);
	var has_margin_field = frappe.meta.has_field(cdt, 'margin_type');

	frappe.model.round_floats_in(item, ["rate", "price_list_rate"]);
	let prev_price_list_rate = item.price_list_rate; // เก็บค่า price_list_rate ก่อนหน้า
	if (item.price_list_rate && !item.blanket_order_rate) {
		if (item.rate > item.price_list_rate && has_margin_field) {
			// if rate is greater than price_list_rate, set margin
			// or set discount
			item.discount_percentage = 0;
			item.margin_type = 'Amount';
			item.margin_rate_or_amount = flt(item.rate - item.price_list_rate,
				precision("margin_rate_or_amount", item));
			item.rate_with_margin = item.rate;
		} else {
			item.discount_percentage = flt((1 - item.rate / item.price_list_rate) * 100.0,
				precision("discount_percentage", item));
			item.discount_amount = flt(item.price_list_rate) - flt(item.rate);
			item.margin_type = '';
			item.margin_rate_or_amount = 0;
			item.rate_with_margin = 0;
		}
	} else {
		item.discount_percentage = 0.0;
		item.margin_type = '';
		item.margin_rate_or_amount = 0;
		item.rate_with_margin = 0;
	}
	item.base_rate_with_margin = item.rate_with_margin * flt(frm.doc.conversion_rate);
	cur_frm.cscript.set_gross_profit(item);
	cur_frm.cscript.calculate_taxes_and_totals();
	cur_frm.cscript.calculate_stock_uom_rate(frm, cdt, cdn);
	item.price_list_rate = prev_price_list_rate; // นำค่าเก่ามาใช้

});

