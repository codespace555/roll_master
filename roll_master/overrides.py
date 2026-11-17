import frappe
from frappe import _

from roll_master.utils import is_fabric_item


def check_fabric_rolls(doc, method=None):
    """Fabric rows must carry a roll (batch)."""
    for row in doc.get("items") or []:
        if not is_fabric_item(row.item_code):
            continue
        if not (row.get("batch_no") or row.get("serial_and_batch_bundle")):
            frappe.throw(
                _("Row {0}: {1} is fabric. Enter rolls using the Rolls button.").format(
                    row.idx, row.item_code
                )
            )


def link_rolls_to_receipt(doc, method=None):
    """Record on each roll (Batch) the Purchase Receipt it came in on."""
    for row in doc.get("items") or []:
        if row.get("batch_no") and is_fabric_item(row.item_code):
            if not frappe.db.get_value("Batch", row.batch_no, "reference_name"):
                frappe.db.set_value("Batch", row.batch_no, {
                    "reference_doctype": doc.doctype,
                    "reference_name": doc.name,
                })
