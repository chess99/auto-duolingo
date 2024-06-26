import unittest

from auto_duolingo.lang_detect import detect_language


class TestLanguageDetection(unittest.TestCase):
    def test_detect_japanese_hiragana(self):
        sentence = "これは日本語の文です。"
        self.assertEqual(detect_language(sentence), "Japanese")

    def test_detect_japanese_katakana(self):
        sentence = "コレは日本語の文です。"
        self.assertEqual(detect_language(sentence), "Japanese")

    def test_detect_japanese_kanji(self):
        sentence = "日本語"
        # Limitation of the heuristic
        self.assertEqual(detect_language(sentence), "Chinese")

    def test_detect_chinese(self):
        sentence = "这是一个测试。"
        self.assertEqual(detect_language(sentence), "Chinese")

    def test_detect_mixed_content(self):
        sentence = "これはテストです。这是一个测试。"
        # Due to the presence of Hiragana/Katakana
        self.assertEqual(detect_language(sentence), "Japanese")


if __name__ == '__main__':
    unittest.main()
