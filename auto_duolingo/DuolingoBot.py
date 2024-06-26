import uiautomator2 as u2

from auto_duolingo.ui_helpers import (
    answer_question,
    is_app_launched,
    is_in_question_screen,
    is_in_unit_selection_screen,
    launch_app,
    select_unit,
    wait_for_tabs,
)


class DuolingoBot:
    """
    A bot for automating tasks in the Duolingo app.

    State transition diagram for the bot:
    """

    def __init__(self, device_id):
        print(f"Connecting to {device_id}...")
        self.d = u2.connect(device_id)
        self.state = "START"

    def run(self):
        print("Bot started running.")
        while True:
            if not is_app_launched(self.d):
                print("App is not launched. Launching app...")
                launch_app(self.d)
            elif is_in_unit_selection_screen(self.d):
                print("In unit selection screen. Selecting unit...")
                select_unit(self.d)
            elif is_in_question_screen(self.d):
                print("In question screen. Answering question...")
                answer_question(self.d)
            else:
                print("Unknown state. Waiting for tabs...")
                wait_for_tabs(self.d)

            if self.state == "END":
                break
        print("Bot finished running.")
