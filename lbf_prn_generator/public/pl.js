frappe.ui.form.on("Pick List", {
  refresh: function (frm) {
    // Add button for Peneus Hub labels
    // Add this to the end of the refresh function in bill_of_landing.js to replace the existing button handlers

    // Add button for Peneus Hub labels
    // setTimeout(function () {
    //   frm.remove_custom_button("Download JSON Labels", "Generate Files");
    // }, 500);
    if (
      frm.doc.custom_service === "Peneus Hub" &&
      frm.doc.custom_p_purpose === "Redelivery" &&
      frm.doc.custom_pl_status === "Completed"
    ) {
      frm.add_custom_button(__("Download PRN File"), function () {
        open_prn_generation_dialog(frm, (label = "pneushub_outbound"));
      });
    }

    // Add button for Tyre Hotel labels
    if (
      frm.doc.service === "Tyre Hotel" &&
      frm.doc.item_details_th &&
      frm.doc.item_details_th.length > 0
    ) {
      if (frm.doc.docstatus === 0 && frm.doc.legal_doc_for_redelivery === 0) {
        frm.add_custom_button(
          __("Download Customer's PRN File"),
          function () {
            open_prn_generation_dialog(frm, (label = "tyrehotel"));
          },
          __("Generate Files"),
        );
      } else {
        frm.add_custom_button(
          __("Download PRN File"),
          function () {
            open_prn_generation_dialog(frm, (label = "tyrehotel"));
          },
          __("Generate Files"),
        );
      }
    }
  },
});

function open_prn_generation_dialog(frm, label) {
  let service = frm.doc.custom_service;

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
        submission_date: data.custom_submission_date,
      };

      const url = frappe.urllib.get_full_url(
        frm.doc.docstatus === 1
          ? `/api/method/lbf_prn_generator.method.generate_prn_pl.generate_json_labels_PL?` +
              `doctype=${encodeURIComponent(args.doctype)}&` +
              `docname=${encodeURIComponent(args.docname)}&` +
              `service_type=${encodeURIComponent(args.service_type)}&` +
              `label_type=${encodeURIComponent(args.label_type)}&` +
              `custom_header=${encodeURIComponent(args.custom_header)}&` +
              `skip_custom_printers=${encodeURIComponent(args.skip_custom_printers)}&` +
              `submission_date=${encodeURIComponent(args.submission_date)}&`
          : `/api/method/lbf_prn_generator.method.json_creator.generate_json_labels?` +
              `doctype=${encodeURIComponent(args.doctype)}&` +
              `docname=${encodeURIComponent(args.docname)}&` +
              `service_type=${encodeURIComponent(args.service_type)}&` +
              `label_type=${encodeURIComponent(args.label_type)}&` +
              `custom_header=${encodeURIComponent(args.custom_header)}&` +
              `skip_custom_printers=${encodeURIComponent(args.skip_custom_printers)}&` +
              `submission_date=${encodeURIComponent(args.submission_date)}`,
      );

      window.open(url);
      dialog.hide();
      // frm.save();
    },
  });

  dialog.show();

  // const initialSkipCustomPrinters = dialog.get_value("skip_custom_printers");
  // const initialLabelType = dialog.get_value("label_type");
  // const showCustomerPrinter =
  //   initialSkipCustomPrinters && initialLabelType === "Tyre Hotel";

  // dialog.set_df_property(
  //   "customer_has_own_printer",
  //   "hidden",
  //   !showCustomerPrinter,
  // );

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
