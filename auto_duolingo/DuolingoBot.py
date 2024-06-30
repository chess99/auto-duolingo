import time

from auto_duolingo.DuolingoUIHelper import DuolingoUIHelper
from auto_duolingo.logger import log_incorrect_answer
from auto_duolingo.question_answer import (
    QuestionType,
    solve_matching_pairs,
    solve_translate_sentence,
    solve_translate_word,
    solve_word_pronunciation,
)
from auto_duolingo.SentencePairDB import SentencePairDB


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

        if "这个怎么读" in challenge_instruction:
            return QuestionType.HOW_TO_PRONOUNCE

        if "选择" in challenge_instruction and "对应的字符" in challenge_instruction:
            return QuestionType.CHOOSE_CORRECT_CHARACTER

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
            self.ui_helper.click_continue_button()

        if question_type == QuestionType.CHOOSE_CORRECT_PICTURE:
            self.ui_helper.deselect_selected_option()
            word = self.ui_helper.extract_origin_sentence()
            options = self.ui_helper.extract_option_list_of_images()
            bounds_to_click = solve_translate_word(word, options)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            self.ui_helper.click_submit_button()
            self.ui_helper.click_continue_button()

        if question_type == QuestionType.CHOOSE_MATCHING_PAIR:
            self.ui_helper.deselect_selected_option()
            words, options = self.ui_helper.extract_matching_pairs()
            bounds_to_click = solve_matching_pairs(words, options)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            # self.ui_helper.click_submit_button() # 不需要点击提交按钮
            self.ui_helper.click_continue_button()

        if question_type == QuestionType.TRANSLATE_SENTENCE:
            self.ui_helper.click_hint_text_if_exists()
            self.ui_helper.reset_selected_answers()
            sentence = self.ui_helper.extract_origin_sentence()
            words = self.ui_helper.extract_alternative_options()
            bounds_to_click = solve_translate_sentence(sentence, words)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            if not bounds_to_click and words:
                # If bounds_to_click is empty, submit directly to skip the question.
                self.ui_helper.perform_clicks_by_bounds([words[0][1]])
            self.ui_helper.click_submit_button()
            result = self.ui_helper.get_answer_status()
            if result.get("original_sentence") and result.get("correct_answer"):
                SentencePairDB().insert_sentence_pair(
                    result["original_sentence"], result["correct_answer"])
            if bounds_to_click and result["status"] == "incorrect":
                log_incorrect_answer(result)
            self.ui_helper.click_continue_button()

        if question_type == QuestionType.HOW_TO_PRONOUNCE:
            self.ui_helper.deselect_selected_option()
            word = self.ui_helper.extract_flashcard_text()
            options = self.ui_helper.extract_option_list_of_word_translation()
            bounds_to_click = solve_word_pronunciation(word, options)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            self.ui_helper.click_submit_button()
            self.ui_helper.click_continue_button()

        if question_type == QuestionType.CHOOSE_CORRECT_CHARACTER:
            self.ui_helper.deselect_selected_option()
            word = self.ui_helper.extract_question_stem_text()
            options = self.ui_helper.extract_option_list_of_scaled_text()
            bounds_to_click = solve_word_pronunciation(word, options)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            self.ui_helper.click_submit_button()
            self.ui_helper.click_continue_button()

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
