frappe.ui.form.on("Material Request Instruction Log", {
  refresh: function (frm) {
    // Add button for Tyre Hotel labels
    if (
      frm.doc.service === "Tyre Hotel" &&
      frm.doc.th_items &&
      frm.doc.th_items.length > 0
    ) {
      if (
        frm.doc.docstatus === 1 &&
        frm.doc.labels_ready_for_print === 1 &&
        frm.doc.material_request_type === "Pick Up"
      ) {
        frm.add_custom_button(__("Download PRN File"), function () {
          open_prn_generation_dialog(frm, (label = "tyrehotel"));
        });
      }
    }
  },
});

function open_prn_generation_dialog(frm, label) {
  let service = frm.doc.service;

  let dialog = new frappe.ui.Dialog({
    title: "PRN Generation",
    size: "small",
    fields: [
      {
        fieldname: "label_type",
        label: "Label Type",
        fieldtype: "Data",
        default: service,
        read_only: 1,
      },
      {
        fieldname: "custom_header",
        label: "Custom Header",
        fieldtype: "Check",
        default: 0,
      },

      {
        fieldname: "skip_custom_printers",
        label: "Custom Printers",
        fieldtype: "Check",
        default: 0,
        onchange: function () {
          const skipCustomPrinters = this.get_value();

          const labelType = dialog.get_value("label_type");

          const shouldShowCustomerPrinter =
            skipCustomPrinters && labelType === "Tyre Hotel";
          dialog.refresh();
        },
      },
    ],

    primary_action_label: __("Download PRN"),

    primary_action: function (data) {
      const args = {
        doctype: frm.doctype,
        docname: frm.docname,
        service_type: service,
        label_type: label,
        custom_header: data.custom_header,
        skip_custom_printers: data.skip_custom_printers,
      };

      const url = frappe.urllib.get_full_url(
        `/api/method/lbf_prn_generator.method.generate_prn_mril.generate_json_labels_MRIL?` +
          `doctype=${encodeURIComponent(args.doctype)}&` +
          `docname=${encodeURIComponent(args.docname)}&` +
          `service_type=${encodeURIComponent(args.service_type)}&` +
          `label_type=${encodeURIComponent(args.label_type)}&` +
          `custom_header=${encodeURIComponent(args.custom_header)}&` +
          `skip_custom_printers=${encodeURIComponent(args.skip_custom_printers)}`,
      );

      window.open(url);
      dialog.hide();
      // frm.save();
    },
  });

  dialog.show();

  // Generate and insert the HTML table with pre-checked serials
  let table_html = `
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th style="width: 5%;"><input type="checkbox" id="select_all"></th>
                    <th>Serial No</th>
                    <th>Batch No</th>
                    <th>Location</th>
                </tr>
            </thead>
            <tbody id="serial_table_body">
            </tbody>
        </table>
    `;
}
