import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed


def process_assist(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]
    return {"type": "WORD_PAIR", "data": [(prompt, correct_choice)]}


def process_listenTap(item):
    metadata = item['metadata']
    translation_data = {
        'sentence': metadata.get('text'),
        'translation': metadata.get('solution_translation'),
        'tokens': metadata.get('tokens'),
        'wrongTokens': metadata.get('wrong_tokens', [])
    }
    return {"type": "SENTENCE_TRANSLATION", "data": [translation_data]}


def process_characterMatch(item):
    pairs = item.get('pairs', [])
    extracted_tokens = [(pair.get('character'), pair.get(
        'transliteration')) for pair in pairs]
    return {"type": "WORD_PAIR", "data": extracted_tokens}


def process_match(item):
    pairs = item.get('pairs', [])
    extracted_tokens = [
        (pair.get('fromToken'), pair.get('learningToken')) for pair in pairs]
    return {"type": "WORD_PAIR", "data": extracted_tokens}


def process_characterIntro(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]
    return {"type": "WORD_PAIR", "data": [(prompt, correct_choice)]}


def process_translate(item):
    metadata = item['metadata']
    translation_data = {
        'sentence': metadata.get('sentence'),
        'translation': metadata.get('translation'),
        'tokens': metadata.get('tokens'),
        'wrongTokens': metadata.get('wrong_tokens', [])
    }
    return {"type": "SENTENCE_TRANSLATION", "data": [translation_data]}


def process_characterSelect(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]['character']
    return {"type": "WORD_PAIR", "data": [(prompt, correct_choice)]}


def process_select(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]['phrase']
    return {"type": "WORD_PAIR", "data": [(prompt, correct_choice)]}


def process_not_implemented(item):
    print(f"Function not implemented for type: {item['type']}")
    return None


def process_challenge_skipping(item):
    pass


# Dispatch dictionary
challenge_processor_map = {
    'characterSelect': process_characterSelect,
    'select': process_select,
    'assist': process_assist,
    'listenTap': process_listenTap,
    'characterMatch': process_characterMatch,
    'match': process_match,
    'characterIntro': process_characterIntro,
    'translate': process_translate,
    'selectPronunciation': process_challenge_skipping,
}


def deduplicate_word_pairs(word_pairs):
    """
    Deduplicates word pairs, treating pairs as equal regardless of order.
    """
    unique_pairs = set()
    for pair in word_pairs:
        # Normalize the pair to ensure order does not matter
        normalized_pair = tuple(sorted(pair))
        unique_pairs.add(normalized_pair)
    # Convert back to list of tuples for consistency
    return list(unique_pairs)


def deduplicate_sentence_translations(translation_data_list):
    unique_translations = set()
    deduplicated_list = []
    for data in translation_data_list:
        identifier = (data['sentence'], data['translation'])
        if identifier not in unique_translations:
            unique_translations.add(identifier)
            deduplicated_list.append(data)
    return deduplicated_list


def process_session_data_from_file(file_path):
    results = defaultdict(list)  # Initialize a collection to store results
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            challenges = data.get('challenges', [])

            for challenge in challenges:
                type_name = challenge['type']
                if type_name in challenge_processor_map:
                    result = challenge_processor_map[type_name](challenge)
                    if result is not None:
                        # Check if result["data"] is a list and flatten it if so
                        if isinstance(result["data"], list):
                            results[result["type"]].extend(result["data"])
                        else:
                            results[result["type"]].append(result["data"])
                else:
                    print(f"No process function for type: {type_name}")
    except json.JSONDecodeError:
        print(f"File {file_path} does not contain valid JSON.")
    return results  # Return the collected results


def process_all_sessions(directory_path):
    all_results = defaultdict(list)
    files_found = False  # Flag to track if any files are found

    def process_file(file_path):
        print(f"Processing {file_path}")
        return process_session_data_from_file(file_path)

    # Create a list to hold futures
    futures = []
    with ThreadPoolExecutor() as executor:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".json"):
                    files_found = True  # Set flag to True when a file is found
                    file_path = os.path.join(root, file)
                    # Submit the task for processing the file
                    future = executor.submit(process_file, file_path)
                    futures.append(future)

        # If no files were found, print a warning in yellow
        if not files_found:
            print(
                f"\033[93mWarning: No .json files found in the specified directory: {directory_path}\033[0m")

        # Collect results as tasks complete
        for future in as_completed(futures):
            results = future.result()
            for result_type, data_list in results.items():
                all_results[result_type].extend(data_list)

    # Deduplicate word pairs before returning
    if "WORD_PAIR" in all_results:
        all_results["WORD_PAIR"] = deduplicate_word_pairs(
            all_results["WORD_PAIR"])

    # Deduplicate sentence translations before returning
    if "SENTENCE_TRANSLATION" in all_results:
        all_results["SENTENCE_TRANSLATION"] = deduplicate_sentence_translations(
            all_results["SENTENCE_TRANSLATION"])

    return all_results
