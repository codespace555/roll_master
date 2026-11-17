app_name = "roll_master"
app_title = "Roll Master"
app_publisher = "Apnemy Technologies"
app_description = "Roll-wise fabric receipt, issue and stock reporting for ERPNext"
app_email = "ap@apnemy.com"
app_license = "mit"
required_apps = ["erpnext"]

# Custom fields are created/updated on install and on every migrate
after_install = "roll_master.install.setup_fields"
after_migrate = "roll_master.install.setup_fields"

# Roll popups (placeholders for now)
doctype_js = {
    "Purchase Receipt": "public/js/purchase_receipt.js",
    "Stock Entry": "public/js/stock_entry.js",
}

# Drafts (e.g. created by OCR) can be saved without rolls; submit needs rolls.
doc_events = {
    "Purchase Receipt": {
        "before_submit": "roll_master.overrides.check_fabric_rolls",
        "on_submit": "roll_master.overrides.link_rolls_to_receipt",
    },
    "Stock Entry": {"before_submit": "roll_master.overrides.check_fabric_rolls"},
}
