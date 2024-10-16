import time
import xml.etree.ElementTree as ET

from auto_duolingo.constants import QuestionType
from auto_duolingo.logger import log_incorrect_answer
from auto_duolingo.question_answer import (
    solve_matching_pairs,
    solve_translate_sentence,
    solve_translate_word,
    solve_word_pronunciation,
)
from auto_duolingo.ui_helper.constants import BTN_HINT_TEXT
from auto_duolingo.ui_helper.DuolingoUIHelper import DuolingoUIHelper
from auto_duolingo.ui_helper.ui_info_extractor import (
    detect_question_type,
    extract_alternative_options,
    extract_flashcard_text,
    extract_matching_pairs,
    extract_option_list_of_images,
    extract_option_list_of_scaled_text,
    extract_option_list_of_word_translation,
    extract_origin_sentence,
    extract_question_stem_text,
    extract_selected_options,
    get_answer_status,
    get_continue_button_bounds,
    is_app_launched,
    is_element_present,
    is_in_no_hearts_screen,
    is_in_question_screen,
    is_in_unit_selection_screen,
    is_in_word_match_madness_screen,
    is_listening_question,
)
from db.SentencePairDB import SentencePairDB


class DuolingoBot:
    """
    A bot for automating tasks in the Duolingo app.
    """

    def __init__(self):
        self.state = "START"
        self.ui_helper = DuolingoUIHelper()

    def answer_question(self, tree: ET.ElementTree):
        if is_listening_question(tree):
            print("Listening question detected, skipping...")
            self.ui_helper.skip_listening_question()

        is_continuous_mode = is_in_word_match_madness_screen(tree)
        selected_options = extract_selected_options(tree)
        if selected_options and not is_continuous_mode:
            print("Resetting selected options...")
            bounds_list = [option[1] for option in selected_options]
            bounds_list.reverse()
            self.ui_helper.perform_clicks_by_bounds(bounds_list)
            tree = self.ui_helper.get_current_screen()

        question_type = detect_question_type(tree)
        print(f"question_type: {question_type}")

        if question_type == QuestionType.UNKNOWN:
            print("Unknown question type. Skipping...")
            return

        if question_type == QuestionType.CHOOSE_CORRECT_TRANSLATION:
            word = extract_origin_sentence(tree)
            options = extract_option_list_of_word_translation(tree)
            bounds_to_click = solve_translate_word(word, options)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            self.ui_helper.click_submit_button()

        if question_type == QuestionType.CHOOSE_CORRECT_PICTURE:
            word = extract_origin_sentence(tree)
            options = extract_option_list_of_images(tree)
            bounds_to_click = solve_translate_word(word, options)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            self.ui_helper.click_submit_button()

        if question_type == QuestionType.CHOOSE_MATCHING_PAIR:
            words, options = extract_matching_pairs(tree)
            bounds_to_click = solve_matching_pairs(
                words, options, disable_inference=is_continuous_mode
            )
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)

        if question_type == QuestionType.TRANSLATE_SENTENCE:
            if is_element_present(tree, BTN_HINT_TEXT):
                self.ui_helper.click_element_if_exists([BTN_HINT_TEXT])
            sentence = extract_origin_sentence(tree)
            words = extract_alternative_options(tree)
            bounds_to_click = solve_translate_sentence(sentence, words)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            if not bounds_to_click and words:
                # If bounds_to_click is empty, submit directly to skip the question.
                self.ui_helper.perform_clicks_by_bounds([words[0][1]])
            self.ui_helper.click_submit_button()

            self.ui_helper.wait_answer_result()
            newTree = self.ui_helper.get_current_screen()
            result = get_answer_status(newTree)
            if result.get("original_sentence") and result.get("correct_answer"):
                SentencePairDB().insert_sentence_pair(
                    result["original_sentence"], result["correct_answer"]
                )
            if bounds_to_click and result["status"] == "incorrect":
                log_incorrect_answer(result)

        if question_type == QuestionType.HOW_TO_PRONOUNCE:
            word = extract_flashcard_text(tree)
            options = extract_option_list_of_word_translation(tree)
            bounds_to_click = solve_word_pronunciation(word, options)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            self.ui_helper.click_submit_button()

        if question_type == QuestionType.CHOOSE_CORRECT_CHARACTER:
            word = extract_question_stem_text(tree)
            options = extract_option_list_of_scaled_text(tree)
            bounds_to_click = solve_word_pronunciation(word, options)
            self.ui_helper.perform_clicks_by_bounds(bounds_to_click)
            self.ui_helper.click_submit_button()

    def run(self):
        print("Bot started running.")
        while True:
            tree = self.ui_helper.get_current_screen()
            continue_button_bounds = get_continue_button_bounds(tree)

            if not is_app_launched(tree):
                print("App is not launched. Launching app...")
                self.ui_helper.launch_app()

            elif continue_button_bounds:
                print("Waiting for continue button. Clicking continue button...")
                self.ui_helper.perform_clicks_by_bounds(
                    [continue_button_bounds])

            elif is_in_unit_selection_screen(tree):
                print("In unit selection screen. Selecting unit...")
                self.ui_helper.select_unit()

            elif is_in_question_screen(tree):
                print("In question screen. Answering question...")
                self.answer_question(tree)

            elif is_in_no_hearts_screen(tree):
                print("No hearts.")
                self.state = "END"

            else:
                print("Unknown state. Resting for 1 second...")
                time.sleep(1)

            if self.state == "END":
                break
        print("Bot finished running.")
