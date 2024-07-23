import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple

from auto_duolingo.constants import QuestionType
from auto_duolingo.ui_helper.constants import (
    CONTINUE_BUTTON_IDS,
    ELEMENTS_OF_LISTENING_QUESTION,
    ELEMENTS_OF_QUESTION_SCREEN,
    ELEMENTS_OF_UNIT_SELECTION,
)


def _bounds_str_to_dict(bounds_str: str) -> dict:
    """
    Parses a string representing bounds in the format "[x1,y1][x2,y2]"
    and returns a dictionary with keys 'left', 'top', 'right', and 'bottom',
    corresponding to x1, y1, x2, and y2 respectively.
    """
    # Extract numbers from the string
    numbers = [int(num) for num in re.findall(r'\d+', bounds_str)]
    # Assign extracted numbers to the respective positions
    return {'left': numbers[0], 'top': numbers[1], 'right': numbers[2], 'bottom': numbers[3]}


def is_element_present(tree: ET.ElementTree, element_id: str) -> bool:
    return tree.find(f".//*[@resource-id='{element_id}']") is not None


def is_app_launched(tree: ET.ElementTree) -> bool:
    # Step 1: Find all elements in the tree
    all_elements = tree.findall(".//*")

    # Step 2: Check each element for the 'package' attribute equal to "com.duolingo"
    for element in all_elements:
        if element.attrib.get('package') == "com.duolingo":
            return True  # Found an element with the package attribute "com.duolingo"

    # Step 3: If no element with the 'package' attribute "com.duolingo" was found, return False
    return False


def is_in_unit_selection_screen(tree: ET.ElementTree) -> bool:
    return any(tree.find(f".//*[@resource-id='{element}']") is not None for element in ELEMENTS_OF_UNIT_SELECTION)


def get_continue_button_bounds(tree: ET.ElementTree) -> Optional[str]:
    for button_id in CONTINUE_BUTTON_IDS:
        xpath_query = f".//*[@resource-id='{button_id}']"
        element = tree.find(xpath_query)
        if element is not None:
            return _bounds_str_to_dict(element.attrib['bounds'])
    return None


def is_in_question_screen(tree: ET.ElementTree) -> bool:
    return any(tree.find(f".//*[@resource-id='{element}']") is not None for element in ELEMENTS_OF_QUESTION_SCREEN)


def is_listening_question(tree: ET.ElementTree) -> bool:
    return any(tree.find(f".//*[@resource-id='{element}']") is not None for element in ELEMENTS_OF_LISTENING_QUESTION)


def extract_challenge_instruction(tree: ET.ElementTree) -> str:
    """Extract challenge instruction for a challenge question using a single UI dump."""
    instruction_element = tree.find(
        ".//*[@resource-id='com.duolingo:id/challengeInstruction']"
    )
    if instruction_element is not None:
        instruction = instruction_element.attrib.get("text", "")
        return instruction
    else:
        return ""  # Return an empty string if the element does not exist


def extract_origin_sentence(tree: ET.ElementTree) -> str:
    sentence_element = tree.find(
        ".//*[@resource-id='com.duolingo:id/hintablePrompt']")
    if sentence_element is not None:
        return sentence_element.attrib.get("text", "")
    else:
        return ""  # Return an empty string if the element does not exist


def extract_option_list_base(
    tree: ET.ElementTree, container_resource_id: str
) -> List[Tuple[str, Dict[str, int]]]:
    options: List[Tuple[str, Dict[str, int]]] = []
    tap_tokens = tree.findall(
        f".//*[@resource-id='{container_resource_id}']//*[@resource-id='com.duolingo:id/tapToken']"
    )
    for token in tap_tokens:
        option_text_element = token.find(
            ".//*[@resource-id='com.duolingo:id/optionText']"
        )
        if option_text_element is not None:
            option_text: str = option_text_element.attrib.get("text", "")
            bounds = _bounds_str_to_dict(option_text_element.attrib["bounds"])
            option: Tuple[str, Dict[str, int]] = (option_text, bounds)
            options.append(option)
    return options


def extract_selected_options(tree: ET.ElementTree):
    return extract_option_list_base(tree, "com.duolingo:id/guessContainer")


def extract_alternative_options(tree: ET.ElementTree):
    options = extract_option_list_base(
        tree, "com.duolingo:id/optionsContainer")
    if not options:
        options = extract_option_list_base(tree, "com.duolingo:id/tapOptions")
    return options


def detect_question_type(tree: ET.ElementTree) -> QuestionType:
    """Convert challenge instruction to question type."""

    challenge_instruction = extract_challenge_instruction(tree)

    if challenge_instruction == "选择正确的翻译":
        return QuestionType.CHOOSE_CORRECT_TRANSLATION
    if challenge_instruction == "选择对应的图片":
        return QuestionType.CHOOSE_CORRECT_PICTURE
    if challenge_instruction == "选择配对":
        return QuestionType.CHOOSE_MATCHING_PAIR
    if challenge_instruction == "翻译这句话":
        return QuestionType.TRANSLATE_SENTENCE
    if "这个怎么读" in challenge_instruction:
        return QuestionType.HOW_TO_PRONOUNCE
    if "选择" in challenge_instruction and "对应的字符" in challenge_instruction:
        return QuestionType.CHOOSE_CORRECT_CHARACTER
    return QuestionType.UNKNOWN


def is_in_word_match_madness_screen(tree: ET.ElementTree) -> bool:
    """ "单词配对乐" """
    return tree.find(".//*[@resource-id='com.duolingo:id/comboIndicatorText']") is not None


def extract_matching_pairs(tree: ET.ElementTree):
    """Extract matching pairs for matching questions using a single UI dump."""

    option_text_elements = tree.findall(
        ".//*[@resource-id='com.duolingo:id/optionText']")

    words = []
    options = []
    for index, element in enumerate(option_text_elements):
        text = element.attrib['text']
        bounds = _bounds_str_to_dict(element.attrib['bounds'])

        if index % 2 == 0:  # Even indices are original words
            words.append((text, bounds))
        else:  # Odd indices are translation options
            options.append((text, bounds))

    return words, options
