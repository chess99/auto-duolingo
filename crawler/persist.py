import json
import logging
import os
from typing import List, TypedDict

from crawler.session_process import (
    deduplicate_sentence_translations,
    deduplicate_word_pairs,
)
from db.SentencePairDB import SentencePairDB
from db.WordPairsDB import WordPairsDB


def save_results_to_db(all_results):
    word_pairs_db = WordPairsDB()
    sentence_pair_db = SentencePairDB()
    result_summary = {}  # Dictionary to store the summary of results

    for result_type, data_list in all_results.items():
        success_count = 0  # Initialize success count for each result type

        if result_type == "WORD_PAIR":
            for data in data_list:
                prompt, correct_choice = data
                lastrowid = word_pairs_db.insert_word_pair(
                    [prompt, correct_choice])
                success_count += 1 if lastrowid > 0 else 0
        elif result_type == "SENTENCE_TRANSLATION":
            for data in data_list:
                success_count += sentence_pair_db.insert_sentence_pair(
                    data['sentence'], data['translation'], data.get('source', ""))

        # Store the result summary instead of printing immediately
        result_summary[result_type] = (len(data_list), success_count)

    # After all types are processed, print the summary for each result type
    for result_type, (total, success) in result_summary.items():
        print(f"{result_type}: {total} items")
        print(f"{result_type}: {success} successfully inserted/updated")


def stringify_keys(data):
    if isinstance(data, dict):
        return {str(key): stringify_keys(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [stringify_keys(item) for item in data]
    else:
        return data


COURSE_DATA_JSON_PATH = "data/course_zs_ja.json"


def save_results_to_json(all_results, reset=False):
    logging.basicConfig(level=logging.DEBUG)

    if not reset and os.path.exists(COURSE_DATA_JSON_PATH):
        logging.debug("Merging with existing data")
        with open(COURSE_DATA_JSON_PATH, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)

        print(f"existing_data: {len(existing_data.get('WORD_PAIR', []))}")
        print(f"all_results: {len(all_results.get('WORD_PAIR', []))}")

        # Merge and deduplicate
        merged_word_pairs = deduplicate_word_pairs(existing_data.get(
            "WORD_PAIR", []) + all_results.get("WORD_PAIR", []))
        merged_sentence_translations = deduplicate_sentence_translations(existing_data.get(
            "SENTENCE_TRANSLATION", []) + all_results.get("SENTENCE_TRANSLATION", []))

        # Calculate the number of new items added after deduplication
        new_word_pairs_count = len(
            merged_word_pairs) - len(existing_data.get("WORD_PAIR", []))
        new_sentence_translations_count = len(
            merged_sentence_translations) - len(existing_data.get("SENTENCE_TRANSLATION", []))

        merged_data = {
            "WORD_PAIR": merged_word_pairs,
            "SENTENCE_TRANSLATION": merged_sentence_translations,
        }
    else:
        logging.debug("Resetting the data")
        merged_data = all_results
        # For reset case, all data is considered new
        new_word_pairs_count = len(all_results.get("WORD_PAIR", []))
        new_sentence_translations_count = len(
            all_results.get("SENTENCE_TRANSLATION", []))

    logging.debug(f"New word pairs added: {new_word_pairs_count}")
    logging.debug(
        f"New sentence translations added: {new_sentence_translations_count}")

    with open(COURSE_DATA_JSON_PATH, 'w', encoding='utf-8') as json_file:
        json.dump(stringify_keys(merged_data), json_file,
                  ensure_ascii=False, indent=4)


class SentencePair(TypedDict):
    sentence: str
    translation: str
    tokens: List[str]
    wrongTokens: List[str]


def get_cached_sentence_pairs() -> List[SentencePair]:
    try:
        with open(COURSE_DATA_JSON_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get('SENTENCE_TRANSLATION', [])
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist


def get_cached_word_pairs():
    try:
        with open(COURSE_DATA_JSON_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get('WORD_PAIR', [])
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist
