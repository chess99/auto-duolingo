from enum import Enum
from typing import Dict, List, Tuple

from auto_duolingo.string_match import sort_substrings
from auto_duolingo.translate_llm import (
    generate_sorted_sentence,
    pick_corresponding_pronunciation,
    pick_semantically_matching_word,
    sort_translations_by_original_order,
)
from db.SentencePairDB import SentencePairDB
from db.WordPairsDB import WordPairsDB


class QuestionType(Enum):
    UNKNOWN = 0
    # "翻译这句话"
    TRANSLATE_SENTENCE = 2
    # "请选择正确的翻译", 一个单词, 三个翻译选项选择一个
    CHOOSE_CORRECT_TRANSLATION = 3
    # "选择对应的图片", 一个单词, 四个图片选项选择一个
    CHOOSE_CORRECT_PICTURE = 4
    # "选择配对", 左边五个原词, 从右边五个词中选择对应的翻译
    CHOOSE_MATCHING_PAIR = 5
    # "这个怎么读？"
    HOW_TO_PRONOUNCE = 6
    # "选择 “xxxx” 对应的字符", 一个平假名单词, 四个汉字选项选择一个
    CHOOSE_CORRECT_CHARACTER = 7


def map_options_to_bounds(sorted_options, options_with_bounds):
    options_with_bounds_dicts = [{'option': option, 'bounds': bounds,
                                  'processed': False} for option, bounds in options_with_bounds]
    bounds_to_click = []
    for option in sorted_options:
        for option_dict in options_with_bounds_dicts:
            if option_dict['option'] == option and not option_dict['processed']:
                bounds_to_click.append(option_dict['bounds'])
                option_dict['processed'] = True  # Mark as processed
                break  # Move to the next word in sorted_options
    return bounds_to_click


def solve_translate_sentence(sentence: str, options_with_bounds: List[Tuple[str, Dict[str, int]]]):
    db_instance = SentencePairDB()
    translation = db_instance.get_complementary_sentence(sentence)

    if translation is not None:
        print(f"Translation found in the database: {translation}")
        sorted_substrings, unmatched = sort_substrings(
            translation, [substring for substring, _ in options_with_bounds])

    if translation is None:
        sorted_substrings = generate_sorted_sentence(
            sentence, [substring for substring, _ in options_with_bounds])

    print(f"sorted_substrings: {sorted_substrings}")

    bounds_to_click = map_options_to_bounds(
        sorted_substrings, options_with_bounds)

    return bounds_to_click


def solve_translate_word(word: str, options_with_bounds: List[Tuple[str, Dict[str, int]]]):
    # Extract options from options_with_bounds
    options = [option for option, _ in options_with_bounds]

    # Use the tool function to pick the correct translation
    correct_translation = pick_semantically_matching_word(word, options)

    # Find the bounds for the correct translation
    bounds_to_click = []
    for option, bounds in options_with_bounds:
        if option == correct_translation:
            bounds_to_click.append(bounds)
            break

    return bounds_to_click


def solve_word_pronunciation(word: str, options_with_bounds: List[Tuple[str, Dict[str, int]]]):
    # Extract options from options_with_bounds
    options = [option for option, _ in options_with_bounds]

    # Use the tool function to pick the correct pronunciation
    correct_pronunciation = pick_corresponding_pronunciation(word, options)

    # Find the bounds for the correct pronunciation
    bounds_to_click = []
    for option, bounds in options_with_bounds:
        if option == correct_pronunciation:
            bounds_to_click.append(bounds)
            break

    return bounds_to_click


def find_db_matches(original_words, translations):
    db_instance = WordPairsDB()
    db_matches = {}
    for word in original_words:
        related_words = db_instance.query_related_words(word)
        for related_word in related_words:
            if related_word in translations:
                db_matches[word] = related_word
                break
    db_instance.close()
    return db_matches


def solve_matching_pairs(words_with_bounds, options_with_bounds):
    original_words = [word for word, _ in words_with_bounds]
    translations = [option for option, _ in options_with_bounds]

    db_matches = find_db_matches(original_words, translations)
    print(f"db_matches: {db_matches}")

    # Initialize placeholders
    sorted_translations = [None] * len(original_words)
    unmatched_indices = []
    unmatched_words = []
    matched_translations = set()

    # Attempt to match using db_matches
    for i, word in enumerate(original_words):
        if word in db_matches:
            sorted_translations[i] = db_matches[word]
            matched_translations.add(db_matches[word])
        else:
            unmatched_indices.append(i)
            unmatched_words.append(word)

    # Filter translations to exclude those that have been matched
    unmatched_translations = [t for t in translations if t not in matched_translations]

    if unmatched_words:
        # Use sort_translations_by_original_order for unmatched words
        sorted_unmatched_translations = sort_translations_by_original_order(
            unmatched_words, unmatched_translations)

        # Merge db_matches and sort_translations_by_original_order results
        for index, translation in zip(unmatched_indices, sorted_unmatched_translations):
            sorted_translations[index] = translation

    # Use map_options_to_bounds for sorted translations
    sorted_translation_bounds = map_options_to_bounds(
        sorted_translations, options_with_bounds)

    # Directly map original words to their bounds
    original_word_bounds = [bounds for _, bounds in words_with_bounds]

    # Interleave original_word_bounds and sorted_translation_bounds
    bounds_to_click = []
    for original_bound, translation_bound in zip(original_word_bounds, sorted_translation_bounds):
        bounds_to_click.append(original_bound)
        bounds_to_click.append(translation_bound)

    return bounds_to_click
