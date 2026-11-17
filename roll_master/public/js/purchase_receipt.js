// Roll Master - receipt popup
// For fabric items (Item Category = Fabric): ask Tag ID / No. of Rolls /
// Metres per Roll, create one Batch per roll and split the row into one row per roll.

frappe.ui.form.on("Purchase Receipt", {
    refresh(frm) {
        if (frm.doc.docstatus !== 0) return;
        frm.add_custom_button(__("Enter Rolls"), () => roll_master.pick_row_for_rolls(frm));
    },
});

frappe.ui.form.on("Purchase Receipt Item", {
    item_code(frm, cdt, cdn) {
        // let ERPNext fill rate / uom / warehouse first
        setTimeout(() => roll_master.maybe_open_roll_dialog(frm, cdn), 800);
    },
});

frappe.provide("roll_master");

roll_master.is_fabric = function (item_code) {
    return frappe
        .call({ method: "roll_master.api.check_fabric", args: { item_code } })
        .then((r) => !!r.message);
};

roll_master.maybe_open_roll_dialog = async function (frm, cdn) {
    const row = locals["Purchase Receipt Item"][cdn];
    if (!row || !row.item_code || row.batch_no) return;
    if (await roll_master.is_fabric(row.item_code)) roll_master.open_roll_dialog(frm, row);
};

// "Enter Rolls" button: fabric rows that have no roll yet (e.g. receipts made by OCR)
roll_master.pick_row_for_rolls = async function (frm) {
    const pending = [];
    for (const row of frm.doc.items || []) {
        if (row.item_code && !row.batch_no && (await roll_master.is_fabric(row.item_code))) {
            pending.push(row);
        }
    }
    if (!pending.length) {
        frappe.msgprint(__("No fabric rows without rolls."));
        return;
    }
    if (pending.length === 1) return roll_master.open_roll_dialog(frm, pending[0]);

    const d = new frappe.ui.Dialog({
        title: __("Which row?"),
        fields: [{
            fieldname: "row", fieldtype: "Select", label: __("Fabric row"), reqd: 1,
            options: pending.map((r) => ({ value: r.name, label: `Row ${r.idx}: ${r.item_code} (${r.qty})` })),
        }],
        primary_action_label: __("Next"),
        primary_action(v) {
            d.hide();
            roll_master.open_roll_dialog(frm, locals["Purchase Receipt Item"][v.row]);
        },
    });
    d.show();
};

roll_master.open_roll_dialog = function (frm, row) {
    const d = new frappe.ui.Dialog({
        title: __("Rolls for {0}", [row.item_code]),
        size: "large",
        fields: [
            { fieldtype: "HTML", fieldname: "info" },
            {
                fieldname: "lines", fieldtype: "Table", label: __("Packing list"),
                cannot_add_rows: false, in_place_edit: true, reqd: 1,
                fields: [
                    { fieldname: "tag_id", fieldtype: "Data", label: __("Tag ID"), in_list_view: 1, reqd: 1, columns: 3 },
                    { fieldname: "rolls", fieldtype: "Int", label: __("No. of Rolls"), in_list_view: 1, reqd: 1, columns: 2,
                      onchange: () => update_totals() },
                    { fieldname: "metres", fieldtype: "Float", label: __("Metres per Roll"), in_list_view: 1, reqd: 1, columns: 2,
                      onchange: () => update_totals() },
                    { fieldname: "total", fieldtype: "Float", label: __("Total Metres"), in_list_view: 1, read_only: 1, columns: 2 },
                ],
                data: [],
            },
        ],
        primary_action_label: __("Create Rolls"),
        primary_action: () => create(),
    });

    function grid_rows() {
        return d.fields_dict.lines.grid.get_data() || [];
    }

    function update_totals() {
        let rolls = 0, metres = 0;
        grid_rows().forEach((l) => {
            l.total = flt(l.rolls) * flt(l.metres);
            rolls += cint(l.rolls);
            metres += l.total;
        });
        d.fields_dict.lines.grid.refresh();
        // qty 1 is just the default on a new row; only compare against a real qty (e.g. from OCR)
        const invoice_qty = flt(row.qty) > 1 ? flt(row.qty) : 0;
        const diff = invoice_qty ? metres - invoice_qty : 0;
        d.fields_dict.info.$wrapper.html(`
            <div class="text-muted small" style="margin-bottom:8px">
                ${__("Row qty")}: <b>${invoice_qty || "-"}</b> &nbsp;|&nbsp;
                ${__("Rolls")}: <b>${rolls}</b> &nbsp;|&nbsp;
                ${__("Total metres")}: <b>${metres}</b>
                ${diff ? `<span class="text-danger"> &nbsp;(${__("difference")} ${diff > 0 ? "+" : ""}${diff})</span>` : ""}
            </div>`);
        return { rolls, metres };
    }

    async function create() {
        const lines = grid_rows()
            .filter((l) => l.tag_id || l.rolls || l.metres)
            .map((l) => ({ tag_id: (l.tag_id || "").trim(), rolls: cint(l.rolls), metres: flt(l.metres) }));
        if (!lines.length || lines.some((l) => !l.tag_id || l.rolls <= 0 || l.metres <= 0)) {
            frappe.msgprint(__("Fill Tag ID, No. of Rolls and Metres per Roll on every line."));
            return;
        }
        const r = await frappe.call({
            method: "roll_master.api.create_rolls",
            args: {
                item_code: row.item_code,
                lines: JSON.stringify(lines),
                purchase_receipt: frm.is_new() ? null : frm.doc.name,
            },
            freeze: true,
            freeze_message: __("Creating rolls..."),
        });
        if (!r.message || !r.message.length) return;
        roll_master.split_row(frm, row, r.message);
        d.hide();
        frappe.show_alert({ message: __("{0} rolls added", [r.message.length]), indicator: "green" });
    }

    d.fields_dict.lines.grid.add_new_row();
    update_totals();
    d.show();
};

// Replace one row with one row per roll, keeping rate, warehouse, uom etc.
roll_master.split_row = function (frm, row, rolls) {
    const skip = ["name", "idx", "__islocal", "__unsaved", "docstatus", "batch_no",
        "serial_and_batch_bundle", "rejected_serial_and_batch_bundle"];
    const template = {};
    Object.keys(row).forEach((k) => { if (!skip.includes(k)) template[k] = row[k]; });
    const cf = flt(row.conversion_factor) || 1;

    const apply = (target, roll) => {
        Object.assign(target, template, {
            batch_no: roll.batch_no,
            use_serial_batch_fields: 1,
            qty: roll.qty,
            received_qty: roll.qty,
            rejected_qty: 0,
            stock_qty: roll.qty * cf,
            received_stock_qty: roll.qty * cf,
        });
    };

    apply(row, rolls[0]);
    rolls.slice(1).forEach((roll) => {
        const child = frm.add_child("items");
        apply(child, roll);
    });

    // keep the new rows directly under the original row
    const items = frm.doc.items;
    const extra = items.splice(items.length - (rolls.length - 1), rolls.length - 1);
    items.splice(row.idx, 0, ...extra);
    items.forEach((it, i) => (it.idx = i + 1));

    frm.refresh_field("items");
    if (frm.cscript && frm.cscript.calculate_taxes_and_totals) frm.cscript.calculate_taxes_and_totals();
    frm.dirty();
};
