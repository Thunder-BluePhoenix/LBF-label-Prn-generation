from typing_extensions import _F
import frappe
from frappe import _
from frappe.model.document import Document
import os
import random
import string
import unicodedata
import json
import frappe
from io import BytesIO
from ..label_generator import generate_label_file_from_json_payload

def generate_random_string(length=10):
    """Generate a random string for temporary file names"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def remove_accents(text):
    """Remove accents from text and replace special characters"""
    if isinstance(text, str):
        text = text.replace("°", ".")
        return ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))
    return text


def generate_label_json(doc, items, service_type="Peneus Hub", label_type=None, custom_header=False, skip_custom_printers=False,customer_has_own_printer=False):
    """
    Generate label data in JSON format

    Args:
        doc: Frappe document object
        items: List of items to generate labels for
        service_type: Service type ('Peneus Hub' or 'Tyre Hotel')

    Returns:
        dict: JSON-ready dictionary with all label data
    """

    if service_type == "Tyre Hotel":
    # Initialize the result structure
        result = {
            "label_type": "tyrehotel",
            "custom_header": False if custom_header == "0" else True,
            "skip_custom_printers": False if skip_custom_printers == "0" else True,
            "customer_has_own_printer": False if customer_has_own_printer == "0" else True,
            "document_info": {
                "doctype": doc.doctype,
                "docname": doc.name,
                "service_type": service_type,
                "creation_date": str(doc.posting_date)
            },
            "labels": []
        }
    else:
        result = {
            "label_type": label_type,
            "custom_header": False if custom_header == "0" else True,
            "skip_custom_printers": False if skip_custom_printers == "0" else True,

            "document_info": {
                "doctype": doc.doctype,
                "docname": doc.name,
                "service_type": service_type,
                "creation_date": str(doc.posting_date)
            },
            "labels": []
        }


    # Process each item
    for item in items:
        # Get accepted and rejected bundles
        accepted_bundles = (item.get('serial_and_batch_bundle_accepted') or '').split(',')

        # Process each accepted bundle
        for bundle_name in accepted_bundles:
            if not bundle_name.strip():
                continue

            # Get bundle document
            bundle_doc = frappe.get_doc('Serial and Batch Bundle', bundle_name.strip())

            # Process each entry in the bundle
            for index, entry in enumerate(bundle_doc.entries, 1):
                if not entry.serial_no:
                    continue

                # Get serial document
                serial_doc = frappe.get_doc('Serial No', entry.serial_no.strip())

                # Prepare label data
                if service_type == "Peneus Hub":
                    custom_slug = (serial_doc.custom_slug or '').upper()

                    label_data = {
                        "batch_no": serial_doc.batch_no or "",
                        "serial_no": serial_doc.name,
                        "item_code": item.get('item_code') or "",
                        "barcode": serial_doc.custom_barcode or "",
                        "customer": {
                            "name": (serial_doc.custom_customer or "").upper(),
                            "code": (serial_doc.custom_customer_code or "").upper()
                        },
                        "product": {

                            "id": serial_doc.name,
                            "slug": custom_slug,
                            "code": item.get('item_code') or "None",
                            "description": item.item_name,
                            "sku": serial_doc.custom_upc or "None"

                        },
                        "packaging": {
                            "index": index,
                            "total": len(bundle_doc.entries)
                        },
                        "document_reference": doc.name
                    }
                else:  # Tyre Hotel format
                    label_data = {
                        "serial_no": serial_doc.name,
                        "customer": remove_accents((doc.customer or '')[:35]).upper(),
                        "plate": remove_accents(serial_doc.custom_license_plate or '').upper(),
                        "order": {
                            "number": doc.name or '',
                            "date": doc.creation.strftime('%d/%m/%Y') if doc.creation else ''
                        },
                        "vehicle": remove_accents(doc.mezzo or '').upper(),
                        "tyre": {
                            "brand": remove_accents(serial_doc.brand or '').upper(),
                            "model": remove_accents(serial_doc.custom_model or '').upper(),
                            "size": f"{serial_doc.custom_tire_widthmm or ''}/{serial_doc.custom_aspect_ratio or ''}{serial_doc.custom_carcass or ''}{serial_doc.custom_diameterinch or ''} {serial_doc.custom_load_index or ''}{serial_doc.custom_speed_rating or ''}",
                            "type": serial_doc.custom_tyre_type or ''
                        },
                        "details": {
                            "season": (doc.season or '').upper(),
                            "condition": (doc.condition or '').upper()
                        },
                        "barcode": serial_doc.custom_barcode if serial_doc.custom_barcode else '',
                        "packaging": {
                            "index": index,
                            "total": len(bundle_doc.entries)
                        }
                    }

                # Add label data to result
                result["labels"].append(label_data)

    return result


def download_label_json(doc, items=None, service_type="Peneus Hub", label_type=None, custom_header=False, skip_custom_printers=False,customer_has_own_printer=False):
    """
    Generate and download a label file in JSON format

    Args:
        doc: Frappe document object
        items: List of items to print labels for (optional)
        service_type: Service type ('Peneus Hub' or 'Tyre Hotel')

    Returns:
        Response: HTTP response with JSON file download
    """
    if items is None:
        if service_type == "Peneus Hub":
            items = doc.item_details_ph
        else:  # Tyre Hotel
            items = doc.item_details_th

    # Generate the label data
    label_data = generate_label_json(doc, items, service_type, label_type, custom_header, skip_custom_printers,customer_has_own_printer)
    # Convert to JSON string
    # import json

    json_str = json.dumps(label_data, indent=2)


    prn = generate_label_file_from_json_payload(json_str)

    frappe.local.response.filename = f"labels_{doc.name}.prn"
    frappe.local.response.filecontent = prn
    frappe.local.response.type = "binary"


    # Prepare the file for download
    # filename = f"labels_{doc.name}_{generate_random_string()}.json"

    # Set up the response for file download
    # frappe.response['filename'] = filename
    # frappe.response['filecontent'] = json_str
    # frappe.response['type'] = 'download'
    # frappe.response['content_type'] = 'application/json'


@frappe.whitelist()
def generate_json_labels(doctype, docname, service_type="Peneus Hub", label_type=None, custom_header=False, skip_custom_printers=False,customer_has_own_printer=False):
    """
    Generate and download JSON label data for a Bill of Landing document

    Args:
        doctype: Document type
        docname: Document name
        service_type: Service type ('Peneus Hub' or 'Tyre Hotel')

    Returns:
        Response: HTTP response with JSON file download
    """

    try:
        doc = frappe.get_doc(doctype, docname)


        if service_type == "Peneus Hub":
            items = doc.get("item_details_ph")
        else:
            items = doc.get("item_details_th")


        if not items:
            frappe.throw(f"No items found for {service_type}")

        return download_label_json(doc, items, service_type, label_type, custom_header, skip_custom_printers,customer_has_own_printer)

    except Exception as e:
        frappe.log_error(title="JSON Label Generation Error", message=frappe.get_traceback())
        frappe.respond_as_web_page(
            title="Error",
            message=f"Error generating JSON labels: {str(e)}",
            indicator_color="red"
        )
