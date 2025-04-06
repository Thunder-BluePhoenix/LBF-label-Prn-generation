from prn_generator_library import generate_label_file_from_json_payload
import json

# with open("./labels_MAT-PRE-PH-2025-03-00002_9c1tXaaRZp.json") as f:
    # payload = f.read()
    # payload = json.load(f)
payload = None
# Optional: you can pass header_name="pneushub" or "blank"
output_path = generate_label_file_from_json_payload(payload,output_path="./my_output_file.prn")

print(f"Label file saved to: {output_path}")
