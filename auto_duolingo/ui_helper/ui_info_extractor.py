import re
import xml.etree.ElementTree as ET
from typing import Optional

from auto_duolingo.constants import QuestionType


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
    ELEMENTS_OF_UNIT_SELECTION = [
        "com.duolingo:id/tooltip",
        "com.duolingo:id/learnButton",
        "com.duolingo:id/startButton",
        "com.duolingo:id/primaryButton",
        "com.duolingo:id/xpBoostLearnButtonType",  # "开始⚡20经验"
    ]
    return any(tree.find(f".//*[@resource-id='{element}']") is not None for element in ELEMENTS_OF_UNIT_SELECTION)


def get_continue_button_bounds(tree: ET.ElementTree) -> Optional[str]:
    CONTINUE_BUTTON_IDS = [
        "com.duolingo:id/continueButtonGreen",
        "com.duolingo:id/continueButtonYellow",
        "com.duolingo:id/continueButtonRed",
        "com.duolingo:id/coachContinueButton",
        "com.duolingo:id/continueButtonView",  # "领取经验"
        "com.duolingo:id/heartsNoThanks",  # 红心 "不，谢谢"
        "com.duolingo:id/boostsDrawerNoThanksButton",  # 时间宝 "不，谢谢"
        "com.duolingo:id/rampUpQuitEndSession",  # 时间宝 "退出"
        "com.duolingo:id/sessionEndContinueButton",  # 单词配对乐 "继续"
        "com.duolingo:id/matchMadnessStartChallenge",  # 单词配对乐 "开始 +40 经验"
    ]
    for button_id in CONTINUE_BUTTON_IDS:
        xpath_query = f".//*[@resource-id='{button_id}']"
        element = tree.find(xpath_query)
        if element is not None:
            return _bounds_str_to_dict(element.attrib['bounds'])
    return None


def is_in_question_screen(tree: ET.ElementTree) -> bool:
    elements_to_check = [
        "com.duolingo:id/challengeInstruction",
        "com.duolingo:id/submitButton",
        "com.duolingo:id/disableListenButton",
    ]
    return any(tree.find(f".//*[@resource-id='{element}']") is not None for element in elements_to_check)


def is_listening_question(tree: ET.ElementTree) -> bool:
    ELEMENTS_OF_LISTENING_QUESTION = [
        "com.duolingo:id/disableListenButton",
        "com.duolingo:id/continueButtonYellow"
    ]
    return any(tree.find(f".//*[@resource-id='{element}']") is not None for element in ELEMENTS_OF_LISTENING_QUESTION)


def extract_challenge_instruction(tree: ET.ElementTree) -> str:
    """Extract challenge instruction for a challenge question using a single UI dump."""
    instruction_element = tree.find(
        ".//*[@resource-id='com.duolingo:id/challengeInstruction']")
    if instruction_element is not None:
        instruction = instruction_element.attrib.get('text', '')
        return instruction
    else:
        return ""  # Return an empty string if the element does not exist


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
