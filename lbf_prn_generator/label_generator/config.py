import os

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, 'static')

BODY_FILE = os.path.join(STATIC_DIR, 'label_body.prn')
HEADER_FILES = {
    "blank": os.path.join(STATIC_DIR, 'label_header_blank.prn'),
    "tyrehotel": os.path.join(STATIC_DIR, 'label_header_tyrehotel.prn'),
    "pneushub": os.path.join(STATIC_DIR, 'label_header_pneushub.prn'),
}

DEFAULT_OUTPUT_DIR = '/tmp/'