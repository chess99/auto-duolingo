import json


def decode_unicode_sequences_to_file(input_file_path, output_file_path):

    # Step 1: Read the input file
    with open(input_file_path, 'r', encoding='utf-8') as file:
        # Step 2: Parse the JSON content
        data = json.load(file)
        tokens = data['tokens']

    # Step 3: Decoding is automatically handled by Python when loading JSON

    # Step 4: Write the decoded strings to an output file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for token in tokens:
            file.write(f"{token}\n")


# Usage example
decode_unicode_sequences_to_file(
    'language_tokens_ja.json', 'language_tokens_ja_decoded.txt')
