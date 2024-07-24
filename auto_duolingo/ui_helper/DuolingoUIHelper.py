import time
import xml.etree.ElementTree as ET
from typing import Dict, List

import uiautomator2 as u2

from auto_duolingo.ui_helper.constants import (
    ELEMENTS_OF_LISTENING_QUESTION,
    ELEMENTS_OF_UNIT_SELECTION,
)
from auto_duolingo.ui_helper.ui_info_extractor import (
    get_continue_button_bounds,
)
from tools.adb_utils import get_device_id


class DuolingoUIHelper:
    def __init__(self):
        device_id = get_device_id()
        print(f"Connecting to {device_id}...")
        self.d = u2.connect(device_id)

    def get_current_screen(self) -> ET.ElementTree:
        return ET.ElementTree(ET.fromstring(self.d.dump_hierarchy()))

    def wait_for_element_to_appear(self, resource_id, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.d(resourceId=resource_id).exists:
                return True
            time.sleep(0.5)  # Wait for half a second before checking again
        return False

    def click_element_if_exists(self, resource_ids: str) -> bool:
        for resource_id in resource_ids:
            element = self.d(resourceId=resource_id)
            if element.exists:
                element.click()
                break
        time.sleep(0.1)

    def perform_clicks_by_bounds(self, bounds_list: List[Dict[str, int]], interval: float = 0.1):
        for bounds in bounds_list:
            click_x = bounds['left'] + (bounds['right'] - bounds['left']) // 2
            click_y = bounds['top'] + (bounds['bottom'] - bounds['top']) // 2
            self.d.click(click_x, click_y)
            time.sleep(interval)

    def wait_answer_result(self):
        return self.wait_for_element_to_appear("com.duolingo:id/ribbonPrimaryTitle")

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

    def launch_app(self):
        self.d.app_start('com.duolingo')

    def select_unit(self):
        self.click_element_if_exists(ELEMENTS_OF_UNIT_SELECTION)

    def skip_listening_question(self):
        self.click_elements_sequentially(ELEMENTS_OF_LISTENING_QUESTION)

    def click_submit_button(self):
        submit_button_id = "com.duolingo:id/submitButton"
        self.d(resourceId=submit_button_id).click()
        time.sleep(0.1)

    def click_continue_button_by_tree(self, tree: ET.ElementTree):
        bounds = get_continue_button_bounds(tree)
        self.perform_clicks_by_bounds([bounds])
        time.sleep(0.1)

    def click_no_thanks(self) -> bool:
        resource_id = "com.duolingo:id/heartsNoThanks"
        element = self.d(resourceId=resource_id, text="不，谢谢")
        if element.exists:
            element.click()
            return True
        return False
