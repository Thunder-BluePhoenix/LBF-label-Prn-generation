frappe.ui.form.on("Bill Of Landing", {
  refresh: function (frm) {
    // Add button for Peneus Hub labels
    // Add this to the end of the refresh function in bill_of_landing.js to replace the existing button handlers

    // Add button for Peneus Hub labels
    // setTimeout(function () {
    //   frm.remove_custom_button("Download JSON Labels", "Generate Files");
    // }, 500);
    if (
      frm.doc.service === "Peneus Hub" &&
      frm.doc.item_details_ph &&
      frm.doc.item_details_ph.length > 0
    ) {
      frm.add_custom_button(
        __("Download PRN File"),
        function () {
          const args = {
            doctype: frm.doctype,
            docname: frm.docname,
            service_type: "Peneus Hub",
          };
          const url = frappe.urllib.get_full_url(
            `/api/method/lbf_logistica.lbf_logistica.doctype.bill_of_landing.bill_of_landing.generate_json_labels?` +
              `doctype=${encodeURIComponent(args.doctype)}&` +
              `docname=${encodeURIComponent(args.docname)}&` +
              `service_type=${encodeURIComponent(args.service_type)}`,
          );
          window.open(url);
        },
        __("Generate Files"),
      );
    }

    // Add button for Tyre Hotel labels
    if (
      frm.doc.service === "Tyre Hotel" &&
      frm.doc.item_details_th &&
      frm.doc.item_details_th.length > 0
    ) {
      frm.add_custom_button(
        __("Download PRN File"),
        function () {
          open_json_generation_dialog(frm);
        },
        __("Generate Files"),
      );
    }
  },
});

function open_json_generation_dialog(frm) {
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

          dialog.set_df_property(
            "customer_has_own_printer",
            "hidden",
            !skipCustomPrinters,
          );

          // If unchecked, also uncheck 'customer_has_own_printer'
          if (!skipCustomPrinters) {
            dialog.set_value("customer_has_own_printer", 0);
          }

          dialog.refresh();
        },
      },
      {
        fieldname: "customer_has_own_printer",
        label: "Customer Has Own Printer",
        fieldtype: "Check",
        default: 0,
        hidden: 1,
      },
    ],
    primary_action_label: __("Download JSON"),
    primary_action: function (data) {
      if (typeof data.customer_has_own_printer === "undefined") {
        data.customer_has_own_printer = 0;
      }
      const args = {
        doctype: frm.doctype,
        docname: frm.docname,
        service_type: "Tyre Hotel",
        label_type: data.label_type,
        custom_header: data.custom_header,
        skip_custom_printers: data.skip_custom_printers,
        customer_has_own_printer: data.customer_has_own_printer,
      };
      console.log(data);
      const url = frappe.urllib.get_full_url(
        `/api/method/lbf_prn_generator.method.json_creator.generate_json_labels?` +
          `doctype=${encodeURIComponent(args.doctype)}&` +
          `docname=${encodeURIComponent(args.docname)}&` +
          `service_type=${encodeURIComponent(args.service_type)}&` +
          `label_type=${encodeURIComponent(args.label_type)}&` +
          `custom_header=${encodeURIComponent(args.custom_header)}&` +
          `skip_custom_printers=${encodeURIComponent(args.skip_custom_printers)}&` +
          `customer_has_own_printer=${encodeURIComponent(args.customer_has_own_printer)}`,
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
