import frappe # type: ignore

# Hook method
def update_approver(doc, method=None):
	doc.custom_approver = doc.modified_by if doc.modified_by else None
	