import time
from typing import Dict, List, Tuple

import uiautomator2 as u2

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
            "com.duolingo:id/submitButton",
            "com.duolingo:id/disableListenButton",
            "com.duolingo:id/continueButtonYellow"
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

    def extract_sentence(self) -> str:
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
        return self.extract_option_list_base("com.duolingo:id/optionsContainer")

    def perform_clicks_by_bounds(self, bounds_list: List[Dict[str, int]], interval: float = 0.1):
        for bounds in bounds_list:
            click_x = bounds['left'] + (bounds['right'] - bounds['left']) // 2
            click_y = bounds['top'] + (bounds['bottom'] - bounds['top']) // 2
            self.d.click(click_x, click_y)
            time.sleep(interval)

    def reset_selected_answers(self):
        selected_options = self.extract_selected_options()
        bounds_list = [option[1] for option in selected_options]
        bounds_list.reverse()
        self.perform_clicks_by_bounds(bounds_list)


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
