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


def solve_translate_sentence(sentence: str, options_with_bounds: List[Tuple[str, Dict[str, int]]]):
    db_instance = SentencePairDB()
    translation = db_instance.get_complementary_sentence(sentence)

    if translation is not None:
        print(f"Translation found in the database: {translation}")
        sorted_substrings, unmatched = sort_substrings(
            translation,  [substring for substring, _ in options_with_bounds])

    if translation is None:
        sorted_substrings = generate_sorted_sentence(
            sentence, [substring for substring, _ in options_with_bounds])

    print(f"sorted_substrings: {sorted_substrings}")

    # Convert list of tuples to a list of dictionaries to keep track of processed words
    options_with_bounds_dicts = [{'substring': substring, 'bounds': bounds,
                                  'processed': False} for substring, bounds in options_with_bounds]

    # Collect bounds in the order they appear in sorted_boxes
    bounds_to_click = []
    for substring in sorted_substrings:
        for option_dict in options_with_bounds_dicts:
            if option_dict['substring'] == substring and not option_dict['processed']:
                bounds_to_click.append(option_dict['bounds'])
                option_dict['processed'] = True  # Mark as processed
                break  # Move to the next word in sorted_boxes

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


def solve_matching_pairs(words_with_bounds, options_with_bounds):
    original_words = [word for word, _ in words_with_bounds]
    translations = [option for option, _ in options_with_bounds]

    # Assuming sort_translations_by_original_order is correctly implemented and available
    sorted_translations = sort_translations_by_original_order(
        original_words, translations)

    # Map sorted translations back to their bounds
    translation_to_bounds = {
        option: bounds for option, bounds in options_with_bounds}
    sorted_translation_bounds = [
        translation_to_bounds[translation] for translation in sorted_translations]

    # Construct bounds_to_click in the specified order: original word - corresponding translation - and so on
    bounds_to_click = []
    for word_bounds in words_with_bounds:
        bounds_to_click.append(word_bounds[1])  # Add original word bounds
        translation_index = original_words.index(word_bounds[0])
        # Add corresponding translation bounds
        bounds_to_click.append(sorted_translation_bounds[translation_index])

    return bounds_to_click
