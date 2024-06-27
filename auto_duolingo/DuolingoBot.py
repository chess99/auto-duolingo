import time

from auto_duolingo.DuolingoUIHelper import DuolingoUIHelper
from auto_duolingo.lang_detect import detect_language
from auto_duolingo.question_answer import solve_translate_chi_jpn


class DuolingoBot:
    """
    A bot for automating tasks in the Duolingo app.
    """

    def __init__(self):
        self.state = "START"
        self.ui_helper = DuolingoUIHelper()

    def answer_question(self):
        if self.ui_helper.is_listening_question():
            print("Listening question detected, skipping...")
            self.ui_helper.skip_listening_question()

        question_type = self.detect_question_type()
        print(f"question_type: {question_type}")

        if question_type == "translate_chi_to_jpn":
            self.ui_helper.reset_selected_answers()
            sentence = self.ui_helper.extract_sentence()
            words = self.ui_helper.extract_alternative_options()
            bounds_to_click = solve_translate_chi_jpn(sentence, words)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)

        if question_type == "translate_jpn_to_chi":
            self.ui_helper.reset_selected_answers()
            sentence = self.ui_helper.extract_sentence()
            words = self.ui_helper.extract_alternative_options()
            # Implement logic for solving translate_jpn_to_chi

    def detect_question_type(self):
        sentence = self.ui_helper.extract_sentence()
        language = detect_language(sentence)

        if language == "Chinese":
            return "translate_chi_to_jpn"
        elif language == "Japanese":
            return "translate_jpn_to_chi"
        else:
            return "unknown_question_type"

    def run(self):
        print("Bot started running.")
        while True:
            if not self.ui_helper.is_app_launched():
                print("App is not launched. Launching app...")
                self.ui_helper.launch_app()
            elif self.ui_helper.is_in_unit_selection_screen():
                print("In unit selection screen. Selecting unit...")
                self.ui_helper.select_unit()
            elif self.ui_helper.is_in_question_screen():
                print("In question screen. Answering question...")
                self.answer_question()
            else:
                print("Unknown state. Resting for 1 second...")
                time.sleep(1)

            if self.state == "END":
                break
        print("Bot finished running.")
