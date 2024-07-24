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


def is_in_no_hearts_screen(tree: ET.ElementTree) -> bool:
    resource_id = "com.duolingo:id/noHeartsTitle"
    return tree.find(f".//*[@resource-id='{resource_id}']") is not None


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


def extract_option_list(tree: ET.ElementTree, container_resource_id: str, option_text_resource_id: str) -> List[Tuple[str, Dict[str, int]]]:
    """Extract options from a specified container and option text resource IDs."""
    options: List[Tuple[str, Dict[str, int]]] = []

    container = tree.find(f".//*[@resource-id='{container_resource_id}']")
    if container is None:
        return options

    option_text_elements = container.findall(
        f".//*[@resource-id='{option_text_resource_id}']")
    for element in option_text_elements:
        if element is not None:
            option_text: str = element.attrib.get("text", "")
            bounds: Dict[str, int] = _bounds_str_to_dict(
                element.attrib["bounds"])
            option: Tuple[str, Dict[str, int]] = (option_text, bounds)
            options.append(option)
    return options


def extract_selected_options(tree: ET.ElementTree):
    """ 已选的 """
    return extract_option_list(tree, "com.duolingo:id/guessContainer", "com.duolingo:id/optionText")


def extract_alternative_options(tree: ET.ElementTree):
    """ 备选的 """
    options = extract_option_list(
        tree, "com.duolingo:id/optionsContainer", "com.duolingo:id/optionText")
    if not options:
        options = extract_option_list(
            tree, "com.duolingo:id/tapOptions", "com.duolingo:id/optionText")
    return options


def extract_option_list_of_word_translation(tree: ET.ElementTree) -> List[Tuple[str, Dict[str, int]]]:
    return extract_option_list(tree, "com.duolingo:id/options", "com.duolingo:id/optionText")


def extract_option_list_of_images(tree: ET.ElementTree) -> List[Tuple[str, Dict[str, int]]]:
    return extract_option_list(tree, "com.duolingo:id/selection", "com.duolingo:id/imageText")


def extract_option_list_of_scaled_text(tree: ET.ElementTree) -> List[Tuple[str, Dict[str, int]]]:
    return extract_option_list(tree, "com.duolingo:id/selection", "com.duolingo:id/scaledText")


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


def extract_flashcard_text(tree: ET.ElementTree) -> str:
    flashcard_resource_id = "com.duolingo:id/flashcard"
    character_resource_id = "com.duolingo:id/character"
    flashcard_element = tree.find(
        f".//*[@resource-id='{flashcard_resource_id}']")
    if flashcard_element is not None:
        character_element = flashcard_element.find(
            f".//*[@resource-id='{character_resource_id}']")
        if character_element is not None:
            return character_element.attrib.get("text", "")
    return ""


def extract_question_stem_text(tree: ET.ElementTree) -> str:
    challenge_instruction_resource_id = "com.duolingo:id/challengeInstruction"
    challenge_instruction_element = tree.find(
        f".//*[@resource-id='{challenge_instruction_resource_id}']")
    if challenge_instruction_element is not None:
        text = challenge_instruction_element.attrib.get("text", "")
        # Extract text within quotes
        match = re.search(r'“(.+?)”', text)
        if match:
            return match.group(1)
    return ""


def get_answer_status(tree: ET.ElementTree):
    result = {
        "status": "unknown",
        "correct_answer": None,
        "selected_options": None,
        "alternative_options": None,
        "original_sentence": None
    }
    ribbon_primary_title_id = "com.duolingo:id/ribbonPrimaryTitle"
    ribbon_primary_text_id = "com.duolingo:id/ribbonPrimaryText"
    ribbon_primary_title_element = tree.find(
        f".//*[@resource-id='{ribbon_primary_title_id}']")
    if ribbon_primary_title_element is not None:
        status_text = ribbon_primary_title_element.attrib.get("text", "")
        if "不正确" in status_text:
            result["status"] = "incorrect"
            ribbon_primary_text_element = tree.find(
                f".//*[@resource-id='{ribbon_primary_text_id}']")
            if ribbon_primary_text_element is not None:
                result["correct_answer"] = ribbon_primary_text_element.attrib.get(
                    "text", "")
            selected_options = extract_selected_options(tree)
            result["selected_options"] = [option[0]
                                          for option in selected_options]
            alternative_options = extract_alternative_options(tree)
            result["alternative_options"] = [option[0]
                                             for option in alternative_options]
        else:
            result["status"] = "correct"
        result["original_sentence"] = extract_origin_sentence(tree)
    return result
