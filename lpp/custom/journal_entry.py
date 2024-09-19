import frappe # type: ignore

@frappe.whitelist()
def get_journal_entry_naming_series():
    naming_series = frappe.get_meta("Journal Entry").get_field("naming_series").options
    return naming_series.split("\n")
@frappe.whitelist()
def get_journal_types_for_user():
    user_roles = frappe.get_roles(frappe.session.user)
    
    # ดึงรายการ 'Journal Type' ที่มี 'item_role' ตรงกับบทบาทของผู้ใช้
    journal_types = frappe.db.sql("""
        SELECT DISTINCT
            jt.name
        FROM
            `tabJournal Type` jt
        INNER JOIN
            `tabItem Journal Type` ijt ON ijt.parent = jt.name
        WHERE
            ijt.role_code IN %(user_roles)s
    """, {
        'user_roles': user_roles
    }, as_dict=True)
    
    return journal_types
