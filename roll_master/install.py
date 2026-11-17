import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
    "Item": [
        {
            "fieldname": "custom_category",
            "label": "Category",
            "fieldtype": "Select",
            "options": "\nFabric\nTrims\nPacking\nOther",
            "insert_after": "item_group",
            "in_standard_filter": 1,
            "description": "Category = Fabric switches on roll-wise handling for this item",
            "module": "Roll Master",
        },
    ],
    "Batch": [
        {
            "fieldname": "custom_tag_id",
            "label": "Tag ID",
            "fieldtype": "Data",
            "insert_after": "item_name",
            "in_list_view": 1,
            "in_standard_filter": 1,
            "search_index": 1,
            "module": "Roll Master",
        },
        {
            "fieldname": "custom_roll_no",
            "label": "Roll No",
            "fieldtype": "Int",
            "insert_after": "custom_tag_id",
            "in_list_view": 1,
            "module": "Roll Master",
        },
        {
            "fieldname": "custom_metres_per_roll",
            "label": "Metres per Roll",
            "fieldtype": "Float",
            "insert_after": "custom_roll_no",
            "in_list_view": 1,
            "description": "Length of the roll at receipt",
            "module": "Roll Master",
        },
    ],
}


# fields from earlier versions of this app that are no longer used
OBSOLETE_FIELDS = ["Item Group-custom_category"]


def setup_fields():
    create_custom_fields(CUSTOM_FIELDS, update=True)
    copy_category_to_variants()
    for name in OBSOLETE_FIELDS:
        if frappe.db.exists("Custom Field", name):
            frappe.delete_doc("Custom Field", name, ignore_permissions=True)
    frappe.db.commit()


def copy_category_to_variants():
    """Variants inherit Category from their template (Item Variant Settings)."""
    ivs = frappe.get_single("Item Variant Settings")
    if not any(f.field_name == "custom_category" for f in ivs.fields):
        ivs.append("fields", {"field_name": "custom_category"})
        ivs.save(ignore_permissions=True)
