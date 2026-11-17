# Roll-wise Stock Balance (STEP 5, placeholder)
# Plan: untouched rolls (balance == metres per roll) grouped by item + warehouse + tag
# + length; part-used rolls listed one per line with their balance.
from frappe import _


def execute(filters=None):
    columns = [
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
        {"label": _("Tag ID"), "fieldname": "tag_id", "fieldtype": "Data", "width": 100},
        {"label": _("Roll"), "fieldname": "roll", "fieldtype": "Data", "width": 160},
        {"label": _("Rolls"), "fieldname": "rolls", "fieldtype": "Int", "width": 70},
        {"label": _("Metres per Roll"), "fieldname": "metres_per_roll", "fieldtype": "Float", "width": 110},
        {"label": _("Balance (m)"), "fieldname": "balance", "fieldtype": "Float", "width": 110},
    ]
    return columns, []
