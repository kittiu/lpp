import frappe # type: ignore

@frappe.whitelist()
def trigger_notification(docname):
    try:
        # Retrieve the Purchase Order document using the given docname
        doc = frappe.get_doc("Purchase Order", docname)
        
        # Fetch the Notification document by its name
        notification = frappe.get_doc("Notification", "Send to MD For Purchase Order")
        
        # Check if the notification is enabled before sending
        if notification.enabled:
            # Manually trigger the notification by sending it for the current document
            notification.send(doc)
        
        # Return success status
        return {"status": "success", "message": "Notification triggered successfully"}
    
    except Exception as e:
        # Handle exceptions and return the error
        frappe.log_error(frappe.get_traceback(), "Notification Trigger Error")
        return {"status": "failed", "message": str(e)}
