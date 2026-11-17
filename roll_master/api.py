import frappe
from frappe import _
from frappe.utils import flt, cint

from roll_master.utils import is_fabric_item


@frappe.whitelist()
def check_fabric(item_code):
    return is_fabric_item(item_code)


@frappe.whitelist()
def create_rolls(item_code, lines, purchase_receipt=None):
    """Create one Batch per physical roll.

    lines: [{"tag_id": "12345", "rolls": 4, "metres": 52}, ...]
    Returns: [{"batch_no": ..., "qty": ...}, ...] - one entry per roll.
    """
    frappe.has_permission("Batch", "create", throw=True)
    if not is_fabric_item(item_code):
        frappe.throw(_("{0} is not a fabric item").format(item_code))

    out = []
    next_no = {}  # same tag on several lines (different lengths) keeps counting
    for ln in frappe.parse_json(lines):
        tag = (ln.get("tag_id") or "").strip()
        rolls, metres = cint(ln.get("rolls")), flt(ln.get("metres"))
        if not tag or rolls <= 0 or metres <= 0:
            frappe.throw(_("Each line needs Tag ID, No. of Rolls and Metres per Roll"))

        start = next_no.get(tag, 1)
        next_no[tag] = start + rolls
        for n in range(start, start + rolls):
            name = f"{item_code}-{tag}-{n:02d}"
            if frappe.db.exists("Batch", name):
                frappe.throw(_("Roll {0} already exists. Check the Tag ID.").format(name))
            frappe.get_doc({
                "doctype": "Batch",
                "batch_id": name,
                "item": item_code,
                "custom_tag_id": tag,
                "custom_roll_no": n,
                "custom_metres_per_roll": metres,
                "reference_doctype": "Purchase Receipt" if purchase_receipt else None,
                "reference_name": purchase_receipt,
            }).insert()
            out.append({"batch_no": name, "qty": metres})
    return out


@frappe.whitelist()
def get_rolls(item_code, warehouse):
    """Rolls of an item with balance > 0 in a warehouse, with tag and length."""
    from erpnext.stock.doctype.batch.batch import get_batch_qty

    balances = get_batch_qty(item_code=item_code, warehouse=warehouse) or []
    rows = []
    for b in balances:
        if flt(b.get("qty")) <= 0:
            continue
        tag, roll_no, metres = frappe.db.get_value(
            "Batch", b.get("batch_no"),
            ["custom_tag_id", "custom_roll_no", "custom_metres_per_roll"],
        ) or (None, None, None)
        rows.append({
            "batch_no": b.get("batch_no"),
            "tag_id": tag,
            "roll_no": roll_no,
            "metres_per_roll": metres,
            "balance": flt(b.get("qty")),
        })
    return sorted(rows, key=lambda r: (r["tag_id"] or "", r["roll_no"] or 0))
