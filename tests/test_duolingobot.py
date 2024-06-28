import unittest
from unittest.mock import MagicMock, patch

from auto_duolingo.DuolingoBot import DuolingoBot
from auto_duolingo.question_answer import QuestionType


class TestDuolingoBot(unittest.TestCase):
    def setUp(self):
        # Patch the DuolingoUIHelper within DuolingoBot to use a MagicMock instead
        patcher = patch('auto_duolingo.DuolingoBot.DuolingoUIHelper')
        self.MockUIHelper = patcher.start()
        self.addCleanup(patcher.stop)
        self.MockUIHelper.return_value = MagicMock()
        self.bot = DuolingoBot()

    def test_detect_question_type_choose_correct_translation(self):
        self.bot.ui_helper.extract_challenge_instruction.return_value = "选择正确的翻译"
        self.assertEqual(self.bot.detect_question_type(),
                         QuestionType.CHOOSE_CORRECT_TRANSLATION)

    def test_detect_question_type_choose_correct_picture(self):
        self.bot.ui_helper.extract_challenge_instruction.return_value = "选择对应的图片"
        self.assertEqual(self.bot.detect_question_type(),
                         QuestionType.CHOOSE_CORRECT_PICTURE)

    def test_detect_question_type_choose_matching_pair(self):
        self.bot.ui_helper.extract_challenge_instruction.return_value = "选择配对"
        self.assertEqual(self.bot.detect_question_type(),
                         QuestionType.CHOOSE_MATCHING_PAIR)

    def test_detect_question_type_translate_sentence(self):
        self.bot.ui_helper.extract_challenge_instruction.return_value = "翻译这句话"
        self.assertEqual(self.bot.detect_question_type(),
                         QuestionType.TRANSLATE_SENTENCE)

    def test_detect_question_type_unknown(self):
        self.bot.ui_helper.extract_challenge_instruction.return_value = "未知类型"
        self.assertEqual(self.bot.detect_question_type(), QuestionType.UNKNOWN)


if __name__ == '__main__':
    unittest.main()
