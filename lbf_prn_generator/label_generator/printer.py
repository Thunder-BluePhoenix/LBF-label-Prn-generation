import os
import unicodedata
from datetime import datetime
import json
import string
import random
import io
from .config import HEADER_FILES, BODY_FILE, DEFAULT_OUTPUT_DIR

def keygen_rand(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def fmt_upper(value):
    return str(value).upper() if value else ""

def fmt_strip_accents(value):
    value = str(value).encode('utf-8').replace(b"\xc2\xb0", b".").decode('utf-8')
    return ''.join((c for c in unicodedata.normalize('NFD', value) if unicodedata.category(c) != 'Mn'))

def fmt_upper_accents(value):
    return fmt_strip_accents(fmt_upper(value))

def format_group_with_separator(number, total_chars=10, pad_char='0', separator=".", group_size=3):
    """
    Format an integer with padding and a custom grouping separator.

    Args:
        number (int): The number to format.
        total_chars (int): Total number of characters in the output, including padding.
        pad_char (str): Character used for left-padding.
        separator (str): Character used to separate groups.
        group_size (int): Number of digits per group.

    Returns:
        str: Formatted string with padding and separators.

    Example:
        format_group_with_separator(12345, total_chars=10)
        -> '00.012.345'
    """
    padded = str(number).rjust(total_chars, pad_char)
    reversed_chars = padded[::-1]

    grouped = separator.join(
        reversed_chars[i:i + group_size] for i in range(0, len(reversed_chars), group_size)
    )

    result = grouped[::-1]
    if result.startswith(separator):
        result = result[1:]

    return result


LABEL_FIELD_MAP = {
    "tyrehotel": {
        "required": ["plate", "customer", "order", "order.date", "tyre.brand", "tyre.model", "tyre.size", "barcode", "packaging"],
        "mapping": {
            "line_0_1": lambda l, s: fmt_upper_accents(l.get("customer", "")[:35]),
            "line_0_2": lambda l, s: "",
            "package_label": lambda l, s: fmt_upper_accents(l.get("plate", "")),
            "line_1_1": lambda l, s: "ORDINE",
            "line_1_2": lambda l, s: l.get("order", {}).get("number", ""),
            "line_1_3": lambda l, s: "DEL",
            "line_1_4": lambda l, s: datetime.strptime(l.get("order", {}).get("date", ""), '%d/%m/%Y').strftime('%d/%m/%Y') if l.get("order", {}).get("date") else "",
            "line_2_1": lambda l, s: "VEICOLO",
            "line_2_2": lambda l, s: fmt_upper_accents(l.get("vehicle", "")),
            "line_3_1": lambda l, s: "MARCA",
            "line_3_2": lambda l, s: fmt_upper_accents(l.get("tyre", {}).get("brand", "")),
            "line_4_1": lambda l, s: "DISEGNO",
            "line_4_2": lambda l, s: fmt_upper_accents(l.get("tyre", {}).get("model", "")),
            "line_5_1": lambda l, s: "MISURA",
            "line_5_2": lambda l, s: l.get("tyre", {}).get("size", ""),
            "line_6_1": lambda l, s: fmt_upper("/".join([x for x in [l.get("details", {}).get("season"), l.get("tyre", {}).get("type"), l.get("details", {}).get("condition")] if x and x != "Non definito"])),
            "line_6_2": lambda l, s: "",
            "barcode": lambda l, s: l.get("barcode", "").strip("*"),
            "v_line_1": lambda l, s: f"COLLO {l.get('packaging', {}).get('index', 1)}/{l.get('packaging', {}).get('total', 1)}",
            "v_line_2": lambda l, s: ""
        }
    },
    "pneushub_inbound": {
        "required": ["customer.name", "batch_no", "product.description", "product.id", "product.sku", "barcode", "packaging"],
        "mapping": {
            "line_0_1": lambda l, s: "CL :",
            "line_0_2": lambda l, s: fmt_upper_accents(l.get("customer", {}).get("name", "")),
            "package_label": lambda l, s: '{:^{width}}'.format(
                                    '{:,}'.format(int(l.get("batch_no", "BN0").lstrip("BN"))).replace(",", "."),
                                    width=12
                                ),
            "line_1_1": lambda l, s: '{:<}'.format(fmt_upper_accents(l.get("product", {}).get("description", ""))[:40]),
            "line_1_2": lambda l, s: "",
            "line_1_3": lambda l, s: "",
            "line_1_4": lambda l, s: "",
            "line_2_1": lambda l, s: '{:<}'.format(fmt_upper_accents(l.get("product", {}).get("description", ""))[40:80]),
            "line_2_2": lambda l, s: "",
            "line_3_1": lambda l, s: 'ID : ',
            "line_3_2": lambda l, s: format_group_with_separator(l.get("product", {}).get("id", 0)),
            "line_4_1": lambda l, s: 'COD. PR. : ',
            "line_4_2": lambda l, s: "",
            "line_5_1": lambda l, s: 'SKU : ',
            "line_5_2": lambda l, s: l.get("product", {}).get("sku", ""),
            "line_6_1": lambda l, s: 'DOC. :',
            "line_6_2": lambda l, s: l.get("document_reference", {}),
            "barcode": lambda l, s: l.get("barcode", "").strip("*"),
            "v_line_1": lambda l, s: f"COLLO {l.get('packaging', {}).get('index', 1)}/{l.get('packaging', {}).get('total', 1)}",
            "v_line_2": lambda l, s: ""
        }
    },
    "pneushub_outbound": {
        "required": ["customer.name", "shipping_to", "shipping_address.address_line1", "shipping_address.city", "shipping_address.state", "transporter_name", "product.description", "warehouse", "barcode", "packaging"],
        "mapping": {
            "line_0_1": lambda l, s: fmt_upper_accents(l.get("customer", {}).get("name", "")[:35]),
            "line_0_2": lambda l, s: "",
            "package_label": lambda l, s: fmt_upper_accents(l.get("shipping_to", "")[:8]),
            "line_1_1": lambda l, s: "",
            "line_1_2": lambda l, s: "",
            "line_1_3": lambda l, s: "",
            "line_1_4": lambda l, s: "",
            "line_2_1": lambda l, s: "",
            "line_2_2": lambda l, s: "",
            "line_3_1": lambda l, s: "",
            "line_3_2": lambda l, s: "",
            "line_4_1": lambda l, s: "",
            "line_4_2": lambda l, s: "",
            "line_5_1": lambda l, s: "",
            "line_5_2": lambda l, s: "",
            "line_6_1": lambda l, s: "",
            "line_6_2": lambda l, s: "",
            "barcode": lambda l, s: l.get("barcode", "").strip("*"),
            "v_line_1": lambda l, s: f"COLLO {l.get('packaging', {}).get('index', 1)}/{l.get('packaging', {}).get('total', 1)}",
            "v_line_2": lambda l, s: ""
        }
    }
}

def validate_label(label, label_type):
    spec = LABEL_FIELD_MAP.get(label_type)
    if not spec:
        raise ValueError(f"Unsupported label type: {label_type}")

    for field in spec["required"]:
        parts = field.split(".")
        val = label
        for p in parts:
            val = val.get(p) if isinstance(val, dict) else None
        if not val:
            raise ValueError(f"Missing required field '{field}' for {label_type} label.")

def validate_payload(payload):
    def parse_bool(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, int):
            return bool(val)
        if isinstance(val, str):
            return val.lower() in ('1', 'true')
        return False
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be a dictionary.")

    label_type = payload.get("label_type")
    if label_type not in LABEL_FIELD_MAP:
        raise ValueError(f"Invalid or missing 'label_type'. Allowed: {list(LABEL_FIELD_MAP)}")

    document_info = payload.get("document_info")
    if not isinstance(document_info, dict):
        raise ValueError("Missing or invalid 'document_info' object.")

    labels = payload.get("labels")
    if not isinstance(labels, list) or not labels:
        raise ValueError("'labels' must be a non-empty list.")

    try:
        custom_header = parse_bool(payload.get("custom_header", 0))
        skip_custom_printers = parse_bool(payload.get("skip_custom_printers", 0))
    except Exception:
        raise ValueError("'custom_header' and 'skip_custom_printers' must be 0, 1, true or false.")

    return label_type, labels, custom_header, skip_custom_printers

class LabelPrinter:
    def __init__(self, output_path=None):
        self.body_path = BODY_FILE

        if output_path:
            self.output_path = output_path
        else:
            random_name = f"label_{keygen_rand()}.prn"
            self.output_path = os.path.join(DEFAULT_OUTPUT_DIR, random_name)

    def print_labels(self, label_type, json_data, custom_header=False):
        header_key = "blank" if not custom_header else label_type.lower()
        header_path = HEADER_FILES.get(header_key, HEADER_FILES["blank"])

        header = open(header_path, 'rb').read()
        with open(self.body_path, 'r', encoding='utf-8') as f_body:
            body = f_body.read()

        mapping = LABEL_FIELD_MAP[label_type]["mapping"]

        prn_buffer = io.BytesIO()

        with open(self.output_path, 'wb') as f:
            for label in json_data:
                validate_label(label, label_type)
                try:
                    data = {key: func(label, self) for key, func in mapping.items()}
                except Exception as e:
                    raise ValueError(f"Error formatting label fields: {e}")
                rendered_body = body.format(**data)
                prn_buffer.write(header + rendered_body.encode('UTF-8'))
                # f.write(header + rendered_body.encode('utf-8'))

        return prn_buffer.getvalue()

def generate_label_file_from_json(json_input_str, label_type=None, custom_header=False, output_path=None):
    payload = json.loads(json_input_str)
    label_type, labels, custom_header, skip_custom_printers = validate_payload(payload)

    printer = LabelPrinter(output_path=output_path)
    return printer.print_labels(label_type=label_type, json_data=labels, custom_header=custom_header)
