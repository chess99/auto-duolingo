import time
from typing import Dict, List, Tuple

from uiautomator2 import Device

from auto_duolingo.lang_detect import detect_language
from auto_duolingo.question_answer import solve_translate_chi_jpn


def click_elements_sequentially(d: Device, elements: List[str]):
    try:
        for element in elements:
            if d(resourceId=element).wait(timeout=5.0):
                d(resourceId=element).click()
                print(f"{element} clicked successfully.")
            else:
                print(
                    f"{element} not found within the timeout period.")
    except Exception as e:
        print(f"Error clicking on element: {e}")


def is_app_launched(d: Device) -> bool:
    # Retrieve the current UI hierarchy as a string or structured data
    ui_hierarchy = d.dump_hierarchy()

    # Check if 'package="com.duolingo"' is present in the UI hierarchy
    if 'package="com.duolingo"' in ui_hierarchy:
        return True

    return False


# 单元选择界面的元素
ELEMENTS_OF_UNIT_SELECTION = [
    "com.duolingo:id/tooltip",
    "com.duolingo:id/learnButton",
    "com.duolingo:id/startButton",
]


def is_in_unit_selection_screen(d: Device) -> bool:
    return any(d(resourceId=element).exists for element in ELEMENTS_OF_UNIT_SELECTION)


def select_unit(d: Device):
    click_elements_sequentially(d, ELEMENTS_OF_UNIT_SELECTION)


def is_in_question_screen(d: Device) -> bool:
    elements_to_check = [
        "com.duolingo:id/submitButton",
        "com.duolingo:id/disableListenButton",
        "com.duolingo:id/continueButtonYellow"
    ]
    return any(d(resourceId=element).exists for element in elements_to_check)


def launch_app(d: Device):
    d.app_start('com.duolingo')


def wait_for_tabs(d: Device):
    while not d(resourceId="com.duolingo:id/tabs").exists:
        time.sleep(1)


ELEMENTS_OF_LISTENING_QUESTION = [
    "com.duolingo:id/disableListenButton",
    "com.duolingo:id/continueButtonYellow"
]


def is_listening_question(d: Device) -> bool:
    return any(d(resourceId=element).exists for element in ELEMENTS_OF_LISTENING_QUESTION)


def skip_listening_question(d: Device):
    click_elements_sequentially(d, ELEMENTS_OF_LISTENING_QUESTION)


def is_translation_question(d: Device) -> bool:
    translation_instruction_id = "com.duolingo:id/challengeInstruction"
    translation_text = "翻译这句话"
    translation_element = d(resourceId=translation_instruction_id)
    return translation_element.exists and translation_element.get_text() == translation_text


def detect_question_type(d):
    sentence = extract_sentence(d)
    language = detect_language(sentence)

    if language == "Chinese":
        return "translate_chi_to_jpn"
    elif language == "Japanese":
        return "translate_jpn_to_chi"
    else:
        return "unknown_question_type"


def extract_sentence(d: Device) -> str:
    # 搞半天OCR, 发现可以直接提取...
    sentence_resource_id = "com.duolingo:id/hintablePrompt"
    sentence_element = d(resourceId=sentence_resource_id)
    if sentence_element.exists:
        return sentence_element.get_text()
    else:
        return ""


def extract_option_list_base(d: Device, container_resource_id: str) -> List[Tuple[str, Dict[str, int]]]:
    """
    Extracts a list of options from a specified container. This function can be used
    to fetch both selected and alternative options within the Duolingo app.
    """
    options: List[Tuple[str, Dict[str, int]]] = []
    tap_tokens = d(resourceId=container_resource_id).child(
        resourceId="com.duolingo:id/tapToken")
    for token in tap_tokens:
        option_text_element = token.child(
            resourceId="com.duolingo:id/optionText")
        if option_text_element.exists:
            option_text: str = option_text_element.get_text()
            # {'bottom': 938, 'left': 48, 'right': 192, 'top': 782}
            bounds: Dict[str, int] = token.info['bounds']
            option: Tuple[str, Dict[str, int]] = (option_text, bounds)
            options.append(option)
    return options


def extract_selected_options(d):
    return extract_option_list_base(d, "com.duolingo:id/guessContainer")


def extract_alternative_options(d):
    return extract_option_list_base(d, "com.duolingo:id/optionsContainer")


def perform_clicks_by_bounds(d, bounds_list: List[Dict[str, int]], interval: float = 0.1):
    for bounds in bounds_list:
        # Calculate the center of the bounds
        click_x = bounds['left'] + (bounds['right'] - bounds['left']) // 2
        click_y = bounds['top'] + (bounds['bottom'] - bounds['top']) // 2
        # Use the device object to click at the calculated center
        d.click(click_x, click_y)
        # Wait for the specified interval before the next click
        time.sleep(interval)


def reset_selected_answers(d):
    selected_options = extract_selected_options(d)
    bounds_list = [option[1] for option in selected_options]
    bounds_list.reverse()
    perform_clicks_by_bounds(d, bounds_list)


def answer_question(d: Device):
    if is_listening_question(d):
        print("Listening question detected, skipping...")
        skip_listening_question(d)  # TODO: 暂未实现听力题

    question_type = detect_question_type(d)
    print(f"question_type: {question_type}")

    if question_type == "translate_chi_to_jpn":
        reset_selected_answers(d)
        sentence = extract_sentence(d)
        words = extract_alternative_options(d)
        bounds_to_click = solve_translate_chi_jpn(sentence, words)
        perform_clicks_by_bounds(d, bounds_to_click)

    if question_type == "translate_jpn_to_chi":
        reset_selected_answers(d)
        sentence = extract_sentence(d)
        words = extract_alternative_options(d)
        # return solve_translate_jpn_chi(sentence, words)
