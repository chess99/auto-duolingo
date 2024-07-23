import unittest

from auto_duolingo.string_util import sort_substrings


class TestSortSubstrings(unittest.TestCase):
    def test_sorted_substrings(self):
        sentence = "じゃがいもを細かく刻んでください"
        substrings = ['を', '細かく', 'で', 'ください', '大豆', '刻ん', 'じゃがいも']
        expected = (['じゃがいも', 'を', '細かく', '刻ん', 'で', 'ください'], '')
        self.assertEqual(expected, sort_substrings(sentence, substrings))

    def test_partial_match(self):
        sentence = "じゃがいもと大豆"
        substrings = ['じゃがいも', '大豆', '細かく']
        expected = (['じゃがいも', '大豆'], 'と')
        self.assertEqual(expected, sort_substrings(sentence, substrings))

    def test_no_match(self):
        sentence = "全く新しい文"
        substrings = ['じゃがいも', '大豆']
        expected = ([], '全く新しい文')
        self.assertEqual(expected, sort_substrings(sentence, substrings))

    def test_empty_sentence(self):
        sentence = ""
        substrings = ['じゃがいも', '大豆']
        expected = ([], '')
        self.assertEqual(expected, sort_substrings(sentence, substrings))

    def test_empty_substrings(self):
        sentence = "じゃがいもと大豆"
        substrings = []
        expected = ([], 'じゃがいもと大豆')
        self.assertEqual(expected, sort_substrings(sentence, substrings))

    def test_multiple_identical_substrings(self):
        sentence = "りんごりんごとバナナ"
        substrings = ['りんご', 'りんご', 'バナナ']
        expected = (['りんご', 'りんご', 'バナナ'], 'と')
        self.assertEqual(expected, sort_substrings(sentence, substrings))

    def test_identical_substrings_different_positions(self):
        sentence = "りんごとバナナりんご"
        substrings = ['りんご', 'バナナ', 'りんご']
        expected = (['りんご', 'バナナ', 'りんご'], 'と')
        self.assertEqual(expected, sort_substrings(sentence, substrings))

    def test_substrings_unordered(self):
        sentence = "りんごとバナナとメロン"
        substrings = ['メロン', 'りんご', 'バナナ']
        expected = (['りんご', 'バナナ', 'メロン'], 'とと')
        self.assertEqual(expected, sort_substrings(sentence, substrings))

    def test_complex_sentence_with_empty_substring(self):
        sentence = "じゃがいもを細かく刻んでください"
        substrings = ['な', '細かく', '', 'で', 'ください', '大豆', '刻ん', 'じゃがいも']
        expected = (['じゃがいも', '細かく', '刻ん', 'で', 'ください'], 'を')
        self.assertEqual(expected, sort_substrings(sentence, substrings))

    def test_sort_substrings_with_partial_overlap(self):
        sentence = "把书放在书桌上了"
        substrings = ['把', '书', '放在', '书桌上', '了']
        expected = (['把', '书', '放在', '书桌上', '了'], '')
        self.assertEqual(expected, sort_substrings(sentence, substrings))


if __name__ == '__main__':
    unittest.main()
