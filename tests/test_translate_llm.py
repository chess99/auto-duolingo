import unittest

from auto_duolingo.translate_llm import (
    generate_sorted_sentence,
    pick_corresponding_pronunciation,
)


class TestGenerateSortedSentenceWithoutPatch(unittest.TestCase):
    # def test_chinese_to_japanese_translation_correct_order(self):
    #     original_sentence = "我爱编程"
    #     words = ["私は", "プログラミング", "が", "大好きです"]
    #     result = generate_sorted_sentence(original_sentence, words)
    #     expected = ["私は", "プログラミング", "が", "大好きです"]
    #     self.assertEqual(result, expected)

    # def test_japanese_to_chinese_translation_correct_order(self):
    #     original_sentence = "私はプログラミングが大好きです"
    #     words = ["我", "爱", "编程"]
    #     result = generate_sorted_sentence(original_sentence, words)
    #     expected = ["我", "爱", "编程"]
    #     self.assertEqual(result, expected)

    def test_chinese_to_japanese_translation_different_order(self):
        original_sentence = "我喜欢旅游"
        words = ["旅行が", "好きです", "私は"]
        result = generate_sorted_sentence(original_sentence, words)
        expected = ["私は", "旅行が", "好きです"]
        self.assertEqual(result, expected)

    def test_japanese_to_chinese_translation_different_order(self):
        original_sentence = "私はコーヒーを飲むのが好きです"
        words = ["咖啡", "喜欢", "喝", "我"]
        result = generate_sorted_sentence(original_sentence, words)
        expected = ["我", "喜欢", "喝", "咖啡"]
        self.assertEqual(result, expected)

    def test_translation_with_extra_words(self):
        original_sentence = "I love coding and coffee"
        words = ["我", "爱", "编程", "和", "咖啡", "还有", "旅游"]
        result = generate_sorted_sentence(original_sentence, words)
        expected = ["我", "爱", "编程", "和", "咖啡"]
        self.assertEqual(result, expected)

    def test_pick_corresponding_pronunciation(self):
        original_word = "まずしい"
        options = ['嬉しい', '楽しい', '美しい', '貧しい']
        expected = '貧しい'
        result = pick_corresponding_pronunciation(original_word, options)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
