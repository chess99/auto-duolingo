import time

from auto_duolingo.DuolingoUIHelper import DuolingoUIHelper
from auto_duolingo.logger import log_incorrect_answer
from auto_duolingo.question_answer import (
    QuestionType,
    solve_matching_pairs,
    solve_translate_sentence,
    solve_translate_word,
)


class DuolingoBot:
    """
    A bot for automating tasks in the Duolingo app.
    """

    def __init__(self):
        self.state = "START"
        self.ui_helper = DuolingoUIHelper()

    def detect_question_type(self):
        challenge_instruction = self.ui_helper.extract_challenge_instruction()

        if challenge_instruction == "选择正确的翻译":
            return QuestionType.CHOOSE_CORRECT_TRANSLATION

        if challenge_instruction == "选择对应的图片":
            return QuestionType.CHOOSE_CORRECT_PICTURE

        if challenge_instruction == "选择配对":
            return QuestionType.CHOOSE_MATCHING_PAIR

        if challenge_instruction == "翻译这句话":
            return QuestionType.TRANSLATE_SENTENCE

        return QuestionType.UNKNOWN

    def answer_question(self):
        if self.ui_helper.is_listening_question():
            print("Listening question detected, skipping...")
            self.ui_helper.skip_listening_question()

        question_type = self.detect_question_type()
        print(f"question_type: {question_type}")

        if question_type == QuestionType.UNKNOWN:
            print("Unknown question type. Skipping...")
            return

        if question_type == QuestionType.CHOOSE_CORRECT_TRANSLATION:
            self.ui_helper.deselect_selected_option()
            word = self.ui_helper.extract_origin_sentence()
            options = self.ui_helper.extract_option_list_of_word_translation()
            bounds_to_click = solve_translate_word(word, options)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            self.ui_helper.click_submit_button()
            time.sleep(1)
            self.ui_helper.click_continue_button()
            time.sleep(1)

        if question_type == QuestionType.CHOOSE_CORRECT_PICTURE:
            self.ui_helper.deselect_selected_option()
            word = self.ui_helper.extract_origin_sentence()
            options = self.ui_helper.extract_option_list_of_word_translation2()
            bounds_to_click = solve_translate_word(word, options)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            self.ui_helper.click_submit_button()
            time.sleep(1)
            self.ui_helper.click_continue_button()
            time.sleep(1)

        if question_type == QuestionType.CHOOSE_MATCHING_PAIR:
            self.ui_helper.deselect_selected_option()
            words, options = self.ui_helper.extract_matching_pairs()
            bounds_to_click = solve_matching_pairs(words, options)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            # self.ui_helper.click_submit_button() # 不需要点击提交按钮
            time.sleep(1)
            self.ui_helper.click_continue_button()
            time.sleep(1)

        if question_type == QuestionType.TRANSLATE_SENTENCE:
            self.ui_helper.reset_selected_answers()
            sentence = self.ui_helper.extract_origin_sentence()
            words = self.ui_helper.extract_alternative_options()
            bounds_to_click = solve_translate_sentence(sentence, words)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            self.ui_helper.click_submit_button()
            time.sleep(1)
            result = self.ui_helper.get_answer_status()
            if result["status"] == "incorrect":
                log_incorrect_answer(result)
            self.ui_helper.click_continue_button()
            time.sleep(1)

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
            elif self.ui_helper.is_in_no_hearts_screen():
                print("No hearts.")
                self.state = "END"
            elif self.ui_helper.is_waiting_continue():
                print("Waiting for continue button. Clicking continue button...")
                self.ui_helper.click_continue_button()
            else:
                print("Unknown state. Resting for 1 second...")
                time.sleep(1)

            if self.state == "END":
                break
        print("Bot finished running.")
