import os
import json
from label_generator.printer import generate_label_file_from_json

def list_json_files(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]
    for i, file in enumerate(files):
        print(f"{i + 1}: {file}")
    return files

def select_file(files):
    choice = input("Choose the file number or enter a full path: ")
    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(files):
            return files[index]
        else:
            print("Invalid index.")
            return None
    else:
        if os.path.isfile(choice):
            return choice
        else:
            print("File not found.")
            return None

def generate_labels_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            payload = json.load(file)
            print("Labels found in the file:")
            for item in payload:
                print(f"- {item}")

            output_path = generate_label_file_from_json(
                json_input_str=json.dumps(payload)
            )
            print(f"Label file generated: {output_path}")

    except Exception as e:
        print(f"Error processing file: {e}")

def test_run():
    json_dir = os.path.join(os.path.dirname(__file__), 'json')
    print(f"Listing JSON files in directory: {json_dir}")
    json_files = list_json_files(json_dir)

    if not json_files:
        print("No JSON files found in the 'json' directory.")

    filepath = None
    while not filepath:
        filepath = select_file(json_files)

    generate_labels_from_file(filepath)

if __name__ == '__main__':
    test_run()
