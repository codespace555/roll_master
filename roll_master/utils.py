import frappe


def is_fabric_item(item_code):
    """True when the item's Category (Item master) is Fabric."""
    if not item_code:
        return False
    return frappe.get_cached_value("Item", item_code, "custom_category") == "Fabric"
