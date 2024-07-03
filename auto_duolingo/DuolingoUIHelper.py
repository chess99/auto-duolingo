import re
import time
from typing import Dict, List, Tuple

import uiautomator2 as u2

from auto_duolingo.Tabs import Tabs
from tools.adb_utils import get_device_id


class DuolingoUIHelper:
    def __init__(self):
        device_id = get_device_id()
        print(f"Connecting to {device_id}...")
        self.d = u2.connect(device_id)

    def click_elements_sequentially(self, elements: List[str]):
        click_started = False
        try:
            for element in elements:
                if not self.d(resourceId=element).exists and not click_started:
                    continue

                if self.d(resourceId=element).wait(timeout=5.0):
                    click_started = True
                    self.d(resourceId=element).click()
                    print(f"{element} clicked successfully.")
                else:
                    print(f"{element} not found within the timeout period.")
        except Exception as e:
            print(f"Error clicking on element: {e}")

    def is_app_launched(self) -> bool:
        ui_hierarchy = self.d.dump_hierarchy()
        return 'package="com.duolingo"' in ui_hierarchy

    def is_in_unit_selection_screen(self) -> bool:
        return any(self.d(resourceId=element).exists for element in ELEMENTS_OF_UNIT_SELECTION)

    def select_unit(self):
        self.click_elements_sequentially(ELEMENTS_OF_UNIT_SELECTION)

    def is_in_question_screen(self) -> bool:
        elements_to_check = [
            "com.duolingo:id/challengeInstruction",
            "com.duolingo:id/submitButton",
            "com.duolingo:id/disableListenButton",
        ]
        return any(self.d(resourceId=element).exists for element in elements_to_check)

    def launch_app(self):
        self.d.app_start('com.duolingo')

    def wait_for_tabs(self):
        while not self.d(resourceId="com.duolingo:id/tabs").exists:
            time.sleep(1)

    def is_listening_question(self) -> bool:
        return any(self.d(resourceId=element).exists for element in ELEMENTS_OF_LISTENING_QUESTION)

    def skip_listening_question(self):
        self.click_elements_sequentially(ELEMENTS_OF_LISTENING_QUESTION)

    def extract_challenge_instruction(self) -> str:
        """
        eg: "选择正确的翻译"
        """
        challenge_instruction_id = "com.duolingo:id/challengeInstruction"
        challenge_instruction_element = self.d(
            resourceId=challenge_instruction_id)
        if challenge_instruction_element.exists:
            return challenge_instruction_element.get_text()
        else:
            return ""

    def click_element_if_exists(self, resource_id: str) -> bool:
        element = self.d(resourceId=resource_id)
        if element.exists:
            element.click()
            time.sleep(0.1)
            return True
        else:
            return False

    def click_hint_text_if_exists(self) -> bool:
        """ 轻点此处查看词库 """
        return self.click_element_if_exists("com.duolingo:id/hintText")

    def extract_origin_sentence(self) -> str:
        sentence_resource_id = "com.duolingo:id/hintablePrompt"
        sentence_element = self.d(resourceId=sentence_resource_id)
        if sentence_element.exists:
            return sentence_element.get_text()
        else:
            return ""

    def extract_option_list_base(self, container_resource_id: str) -> List[Tuple[str, Dict[str, int]]]:
        options: List[Tuple[str, Dict[str, int]]] = []
        tap_tokens = self.d(resourceId=container_resource_id).child(
            resourceId="com.duolingo:id/tapToken")
        for token in tap_tokens:
            option_text_element = token.child(
                resourceId="com.duolingo:id/optionText")
            if option_text_element.exists:
                option_text: str = option_text_element.get_text()
                bounds: Dict[str, int] = token.info['bounds']
                option: Tuple[str, Dict[str, int]] = (option_text, bounds)
                options.append(option)
        return options

    def extract_selected_options(self):
        return self.extract_option_list_base("com.duolingo:id/guessContainer")

    def extract_alternative_options(self):
        options = self.extract_option_list_base(
            "com.duolingo:id/optionsContainer")
        if not options:
            options = self.extract_option_list_base(
                "com.duolingo:id/tapOptions")
        return options

    def perform_clicks_by_bounds(self, bounds_list: List[Dict[str, int]], interval: float = 0.1):
        for bounds in bounds_list:
            click_x = bounds['left'] + (bounds['right'] - bounds['left']) // 2
            click_y = bounds['top'] + (bounds['bottom'] - bounds['top']) // 2
            self.d.click(click_x, click_y)
            time.sleep(interval)

    def click_submit_button(self):
        submit_button_id = "com.duolingo:id/submitButton"
        self.d(resourceId=submit_button_id).click()
        time.sleep(0.1)

    def is_waiting_continue(self):
        return any(self.d(resourceId=button_id).exists for button_id in CONTINUE_BUTTON_IDS)

    def click_continue_button(self):
        for button_id in CONTINUE_BUTTON_IDS:
            button = self.d(resourceId=button_id)
            if button.exists:
                button.click()
                break
        time.sleep(0.1)

    def reset_selected_answers(self):
        selected_options = self.extract_selected_options()
        bounds_list = [option[1] for option in selected_options]
        bounds_list.reverse()
        self.perform_clicks_by_bounds(bounds_list)

    def extract_option_list(self, container_resource_id: str, option_text_resource_id: str) -> List[Tuple[str, Dict[str, int]]]:
        """Extract options from a specified container and option text resource IDs."""
        options: List[Tuple[str, Dict[str, int]]] = []
        container = self.d(resourceId=container_resource_id)
        option_text_elements = container.child(
            resourceId=option_text_resource_id)
        for element in option_text_elements:
            if element.exists:
                option_text: str = element.get_text()
                bounds: Dict[str, int] = element.info['bounds']
                option: Tuple[str, Dict[str, int]] = (option_text, bounds)
                options.append(option)
        return options

    def extract_option_list_of_word_translation(self) -> List[Tuple[str, Dict[str, int]]]:
        return self.extract_option_list("com.duolingo:id/options", "com.duolingo:id/optionText")

    def extract_option_list_of_images(self) -> List[Tuple[str, Dict[str, int]]]:
        return self.extract_option_list("com.duolingo:id/selection", "com.duolingo:id/imageText")

    def extract_option_list_of_scaled_text(self) -> List[Tuple[str, Dict[str, int]]]:
        return self.extract_option_list("com.duolingo:id/selection", "com.duolingo:id/scaledText")

    def deselect_selected_option(self):
        selected_option_id = "com.duolingo:id/optionText"
        selected_option_element = self.d(
            resourceId=selected_option_id, selected=True)
        if selected_option_element.exists:
            selected_option_element.click()

    def extract_matching_pairs(self):
        """Extract matching pairs for matching questions."""
        option_text_id = "com.duolingo:id/optionText"
        elements = self.d(resourceId=option_text_id)
        words = []
        options = []
        for index, element in enumerate(elements):
            text = element.get_text()
            bounds: Dict[str, int] = element.info['bounds']
            if index % 2 == 0:  # Even indices are original words
                words.append((text, bounds))
            else:  # Odd indices are translation options
                options.append((text, bounds))
        return words, options

    def get_answer_status(self):
        result = {
            "status": "unknown",
            "correct_answer": None,
            "selected_answer": None,
            "original_sentence": None
        }
        ribbon_primary_title_id = "com.duolingo:id/ribbonPrimaryTitle"
        ribbon_primary_text_id = "com.duolingo:id/ribbonPrimaryText"
        ribbon_primary_title_element = self.d(
            resourceId=ribbon_primary_title_id)
        if ribbon_primary_title_element.exists:
            status_text = ribbon_primary_title_element.get_text()
            if "不正确" in status_text:
                result["status"] = "incorrect"
                ribbon_primary_text_element = self.d(
                    resourceId=ribbon_primary_text_id)
                if ribbon_primary_text_element.exists:
                    result["correct_answer"] = ribbon_primary_text_element.get_text()
                # Extract selected options as a list of strings
                selected_options = self.extract_selected_options()
                result["selected_answer"] = [option[0]
                                             for option in selected_options]
            else:
                result["status"] = "correct"
            # Extract the original sentence
            result["original_sentence"] = self.extract_origin_sentence()
        return result

    def is_in_answer_grading_screen(self):
        grading_ribbon_id = "com.duolingo:id/gradingRibbonContainer"
        grading_ribbon_element = self.d(resourceId=grading_ribbon_id)
        return grading_ribbon_element.exists

    def is_in_no_hearts_screen(self) -> bool:
        resource_id = "com.duolingo:id/noHeartsTitle"
        element = self.d(resourceId=resource_id)
        return element.exists

    def click_no_thanks(self) -> bool:
        resource_id = "com.duolingo:id/heartsNoThanks"
        element = self.d(resourceId=resource_id, text="不，谢谢")
        if element.exists:
            element.click()
            return True
        return False

    def extract_flashcard_text(self) -> str:
        flashcard_resource_id = "com.duolingo:id/flashcard"
        character_resource_id = "com.duolingo:id/character"
        flashcard_element = self.d(resourceId=flashcard_resource_id)
        if flashcard_element.exists:
            character_element = flashcard_element.child(
                resourceId=character_resource_id)
            if character_element.exists:
                return character_element.get_text()
        return ""

    def extract_question_stem_text(self) -> str:
        challenge_instruction_resource_id = "com.duolingo:id/challengeInstruction"
        challenge_instruction_element = self.d(
            resourceId=challenge_instruction_resource_id)
        if challenge_instruction_element.exists:
            text = challenge_instruction_element.get_text()
            # Extract text within quotes
            match = re.search(r'“(.+?)”', text)
            if match:
                return match.group(1)
        return ""

    def select_tab(self, tab: Tabs) -> bool:
        element = self.d(resourceId=tab.resource_id)
        if element.exists:
            element.click()
            return True
        return False


# Constants used in the class
ELEMENTS_OF_UNIT_SELECTION = [
    "com.duolingo:id/tooltip",
    "com.duolingo:id/learnButton",
    "com.duolingo:id/startButton",
    "com.duolingo:id/primaryButton",
]

ELEMENTS_OF_LISTENING_QUESTION = [
    "com.duolingo:id/disableListenButton",
    "com.duolingo:id/continueButtonYellow"
]

CONTINUE_BUTTON_GREEN = "com.duolingo:id/continueButtonGreen"
CONTINUE_BUTTON_YELLOW = "com.duolingo:id/continueButtonYellow"
CONTINUE_BUTTON_RED = "com.duolingo:id/continueButtonRed"
CONTINUE_BUTTON_COACH = "com.duolingo:id/coachContinueButton"
CONTINUE_BUTTON_IDS = [
    CONTINUE_BUTTON_GREEN,
    CONTINUE_BUTTON_YELLOW,
    CONTINUE_BUTTON_RED,
    CONTINUE_BUTTON_COACH,
]
