import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

from db.SentencePairDB import SentencePairDB
from db.WordPairsDB import WordPairsDB


class DataType(Enum):
    WORD_PAIR = "word_pair"
    SENTENCE_TRANSLATION = "sentence_translation"


def process_assist(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]
    return {"type": DataType.WORD_PAIR, "data": [(prompt, correct_choice)]}


def process_listenTap(item):
    metadata = item['metadata']
    translation_data = {
        'sentence': metadata.get('text'),
        'translation': metadata.get('solution_translation'),
        'tokens': metadata.get('tokens'),
        # 'learning_language': metadata.get('learning_language'),
        # 'from_language': metadata.get('from_language')
    }
    return {"type": DataType.SENTENCE_TRANSLATION, "data": [translation_data]}


def process_characterMatch(item):
    pairs = item.get('pairs', [])
    extracted_tokens = [(pair.get('character'), pair.get(
        'transliteration')) for pair in pairs]
    return {"type": DataType.WORD_PAIR, "data": extracted_tokens}


def process_match(item):
    pairs = item.get('pairs', [])
    extracted_tokens = [
        (pair.get('fromToken'), pair.get('learningToken')) for pair in pairs]
    return {"type": DataType.WORD_PAIR, "data": extracted_tokens}


def process_characterIntro(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]
    return {"type": DataType.WORD_PAIR, "data": [(prompt, correct_choice)]}


def process_translate(item):
    metadata = item['metadata']
    translation_data = {
        'sentence': metadata.get('sentence'),
        'translation': metadata.get('translation'),
        'tokens': metadata.get('tokens'),
        # # 'learning_language': metadata.get('learning_language'),
        # # 'from_language': metadata.get('from_language')
    }
    return {"type": DataType.SENTENCE_TRANSLATION, "data": [translation_data]}


def process_characterSelect(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]['character']
    return {"type": DataType.WORD_PAIR, "data": [(prompt, correct_choice)]}


def process_select(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]['phrase']
    return {"type": DataType.WORD_PAIR, "data": [(prompt, correct_choice)]}


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
    return results  # Return the collected results


def process_all_sessions(directory_path):
    all_results = defaultdict(list)

    def process_file(file_path):
        print(f"Processing {file_path}")
        return process_session_data_from_file(file_path)

    # Create a list to hold futures
    futures = []
    with ThreadPoolExecutor() as executor:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    # Submit the task for processing the file
                    future = executor.submit(process_file, file_path)
                    futures.append(future)

        # Collect results as tasks complete
        for future in as_completed(futures):
            results = future.result()
            for result_type, data_list in results.items():
                all_results[result_type].extend(data_list)

    # Deduplicate word pairs before returning
    if DataType.WORD_PAIR in all_results:
        all_results[DataType.WORD_PAIR] = deduplicate_word_pairs(
            all_results[DataType.WORD_PAIR])

    # Deduplicate sentence translations before returning
    if DataType.SENTENCE_TRANSLATION in all_results:
        all_results[DataType.SENTENCE_TRANSLATION] = deduplicate_sentence_translations(
            all_results[DataType.SENTENCE_TRANSLATION])

    return all_results


def save_results_to_db(all_results):
    word_pairs_db = WordPairsDB()
    sentence_pair_db = SentencePairDB()
    result_summary = {}  # Dictionary to store the summary of results

    for result_type, data_list in all_results.items():
        success_count = 0  # Initialize success count for each result type

        if result_type == DataType.WORD_PAIR:
            for data in data_list:
                prompt, correct_choice = data
                success_count += word_pairs_db.insert_word_group(
                    [prompt, correct_choice])
        elif result_type == DataType.SENTENCE_TRANSLATION:
            for data in data_list:
                success_count += sentence_pair_db.insert_sentence_pair(
                    data['sentence'], data['translation'], data.get('source', ""))

        # Store the result summary instead of printing immediately
        result_summary[result_type] = (len(data_list), success_count)

    # After all types are processed, print the summary for each result type
    for result_type, (total, success) in result_summary.items():
        print(f"{result_type}: {total} items")
        print(f"{result_type}: {success} successfully inserted/updated")


if __name__ == "__main__":
    sessions_directory = ".temp/sessions/"
    all_results = process_all_sessions(sessions_directory)
    save_results_to_db(all_results)
