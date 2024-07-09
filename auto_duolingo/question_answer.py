from enum import Enum
from typing import Dict, List, Tuple

from auto_duolingo.string_match import sort_substrings
from auto_duolingo.translate_llm import (
    llm_generate_sorted_sentence,
    llm_pick_corresponding_pronunciation,
    llm_pick_semantically_matching_word,
    llm_sort_translations_by_original_order,
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
        sorted_substrings = llm_generate_sorted_sentence(
            sentence, [substring for substring, _ in options_with_bounds])

    print(f"sorted_substrings: {sorted_substrings}")

    bounds_to_click = map_options_to_bounds(
        sorted_substrings, options_with_bounds)

    return bounds_to_click


def solve_translate_word(word: str, options_with_bounds: List[Tuple[str, Dict[str, int]]]):
    options = [option for option, _ in options_with_bounds]

    db_matches = WordPairsDB().find_matches([word], options)
    print(f"db_matches: {db_matches}")

    translation = db_matches.get(word)
    if not translation:
        translation = llm_pick_semantically_matching_word(word, options)

    bounds_to_click = map_options_to_bounds([translation], options_with_bounds)
    return bounds_to_click


def solve_word_pronunciation(word: str, options_with_bounds: List[Tuple[str, Dict[str, int]]]):
    options = [option for option, _ in options_with_bounds]

    db_matches = WordPairsDB().find_matches([word], options)
    print(f"db_matches: {db_matches}")

    translation = db_matches.get(word)
    if not translation:
        translation = llm_pick_corresponding_pronunciation(word, options)

    bounds_to_click = map_options_to_bounds([translation], options_with_bounds)
    return bounds_to_click


def solve_matching_pairs(words_with_bounds, options_with_bounds):
    original_words = [word for word, _ in words_with_bounds]
    option_words = [option for option, _ in options_with_bounds]

    db_matches = WordPairsDB().find_matches(original_words, option_words)
    print(f"db_matches: {db_matches}")

    unmatched_words = [word for word in db_matches if db_matches[word] is None]

    # If unmatched_words length is 1, then we can directly determine the unmatched word in option_words
    if len(unmatched_words) == 1:
        for option in option_words:
            if option not in db_matches.values():
                print(f"Matched '{unmatched_words[0]}' with '{option}'.")
                db_matches[unmatched_words[0]] = option
                unmatched_words = []
                break

    if unmatched_words:
        sorted_translations = llm_sort_translations_by_original_order(
            unmatched_words, [option for option in option_words if option not in db_matches.values()])
        for word, translation in zip(unmatched_words, sorted_translations):
            db_matches[word] = translation
            print(f"Matched '{word}' with '{translation}'.")

    all_words = []
    for word, translation in db_matches.items():
        all_words.append(word)
        all_words.append(translation)

    bounds_to_click = map_options_to_bounds(
        all_words, words_with_bounds + options_with_bounds)

    return bounds_to_click
