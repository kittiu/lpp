app_name = "lpp"
app_title = "LPP"
app_publisher = "Ecosoft"
app_description = "ERPNext for Lamphun Plastpack"
app_email = "kittiu@ecosoft.co.th"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/lpp/css/ui-framework.css"
# app_include_js = "/assets/lpp/js/lpp.js"

# include js, css files in header of web template
# web_include_css = "/assets/lpp/css/lpp.css"
# web_include_js = "/assets/lpp/js/lpp.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "lpp/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Quotation" : "public/js/quotation.js",
    "Purchase Order" : "public/js/purchase_order.js",
    "Purchase Invoice" : "public/js/purchase_invoice.js",
    "Material Request" : "public/js/material_request.js",
    "Stock Entry" : "public/js/stock_entry.js",
    "BOM" : "public/js/bom.js",
    "Work Order" : "public/js/work_order.js",
    "Delivery Note" : "public/js/delivery_note.js",
    "Quality Inspection" : "public/js/quality_inspection.js",
    "Sales Billing" : "public/js/sales_billing.js",
    "Purchase Billing" : "public/js/purchase_billing.js",
    "Journal Entry" : "public/js/journal_entry.js",
    "Withholding Tax Cert": "public/js/withholding_tax_cert.js",
    "Payment Entry": "public/js/payment_entry.js" ,
    "Asset": "public/js/asset.js",
    "Journal Type": "public/js/journal_type.js",
    "Batch" : "public/js/batch.js",
    "Pricing Rule" : "public/js/pricing_rule.js",
    "Item" : "public/js/item.js",
    "Purchase Receipt": "public/js/purchase_receipt.js",
    "Address" : "public/js/address.js",
    "Job Card" : "public/js/job_card.js",
    "Sales Order" : "public/js/sales_order.js"
}
doctype_list_js = {
    "Journal Entry": "public/js/journal_entry_list.js",
    "Payment Entry": "public/js/payment_entry_list.js",
    "Purchase Order": "public/js/purchase_order.js",
    "Material Request": "public/js/material_request.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "lpp/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
    "methods": [
		"qr_demo.qr_code.get_qr_code",
        "lpp.utils.jinja_methods",
	],
	"filters": "lpp.utils.jinja_filters"
}

# Installation
# ------------

# before_install = "lpp.install.before_install"
# after_install = "lpp.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "lpp.uninstall.before_uninstall"
# after_uninstall = "lpp.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "lpp.utils.before_app_install"
# after_app_install = "lpp.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "lpp.utils.before_app_uninstall"
# after_app_uninstall = "lpp.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "lpp.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Quality Inspection" : "lpp.custom.custom_quality_inspection.CustomQualityInspection",
    "Sales Billing" : "lpp.custom.custom_sales_billing.CustomSalesBilling",
    "Purchase Billing" : "lpp.custom.custom_purchase_billing.CustomPurchaseBilling",
    "Batch": "lpp.custom.custom_batch.CustomBatch",
    "Payment Entry": "lpp.custom.custom_payment_entry.CustomPaymentEntry",
    "Item": "lpp.custom.custom_item.CustomItem",
    "Pricing Rule": "lpp.custom.custom_pricing_rule.CustomPricingRule",
    "Purchase Receipt": "lpp.custom.custom_purchase_receipt.CustomPurchaseReceipt",
    "BOM" : "lpp.custom.custom_bom.CustomBOM"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"lpp.tasks.all"
# 	],
# 	"daily": [
# 		"lpp.tasks.daily"
# 	],
# 	"hourly": [
# 		"lpp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"lpp.tasks.weekly"
# 	],
# 	"monthly": [
# 		"lpp.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "lpp.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.controllers.stock_controller.make_quality_inspections": "lpp.custom.custom_quality_inspection.custom_make_quality_inspections",
    "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice" : "lpp.custom.custom_purchase_receipt.make_purchase_invoice"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "lpp.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["lpp.utils.before_request"]
# after_request = ["lpp.utils.after_request"]

# Job Events
# ----------
# before_job = ["lpp.utils.before_job"]
# after_job = ["lpp.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"lpp.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

