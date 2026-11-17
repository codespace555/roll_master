frappe.query_reports["Roll-wise Stock Balance"] = {
    filters: [
        { fieldname: "company", label: __("Company"), fieldtype: "Link", options: "Company",
          default: frappe.defaults.get_user_default("Company"), reqd: 1 },
        { fieldname: "warehouse", label: __("Warehouse"), fieldtype: "Link", options: "Warehouse" },
        { fieldname: "item_code", label: __("Item"), fieldtype: "Link", options: "Item" },
        { fieldname: "tag_id", label: __("Tag ID"), fieldtype: "Data" },
    ],
};
