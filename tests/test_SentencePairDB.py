import os
import unittest

from db.SentencePairDB import SentencePairDB


class TestSentencePairDB(unittest.TestCase):
    test_db_name = 'test_sentence_pairs.db'

    @classmethod
    def setUpClass(cls):
        # Construct the path to the test database file
        cls.current_dir = os.path.dirname(__file__)
        cls.data_folder = os.path.join(cls.current_dir, '..', 'data')
        cls.test_db_name = 'test_sentence_pairs.db'
        cls.test_db_path = os.path.join(cls.data_folder, cls.test_db_name)
        # Ensure the test database does not exist before starting tests
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def setUp(self):
        """Create a new database instance for each test method."""
        self.db = SentencePairDB(self.test_db_name)

    def tearDown(self):
        """Close the database connection and delete the test database after each test method."""
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_insert_new_sentence_pair(self):
        """Test inserting a new sentence pair."""
        original = "Hello, world!"
        translated = "こんにちは、世界！"
        self.db.insert_sentence_pair(original, translated)
        # Assuming there's a method to fetch a sentence pair by original sentence
        result = self.db.get_complementary_sentence(original)
        self.assertEqual(translated, result)

    def test_insert_existing_sentence_pair_no_update(self):
        """Test inserting an existing sentence pair without update."""
        original = "Good morning!"
        translated = "おはようございます！"
        self.db.insert_sentence_pair(original, translated)
        # Attempt to insert the same pair again
        self.db.insert_sentence_pair(original, translated)
        # Verify it does not duplicate
        result = self.db.fetch_all_sentence_pairs()
        self.assertEqual(1, len(result))

    # TODO: Redesign
    # def test_insert_existing_sentence_pair_with_update(self):
    #     """Test updating an existing sentence pair with 'incorrect_answer' source."""
    #     original = "Good night!"
    #     translated = "おやすみなさい！"
    #     self.db.insert_sentence_pair(original, translated)
    #     # Insert with 'incorrect_answer' to trigger update
    #     updated_translated = "こんばんは！"
    #     self.db.insert_sentence_pair(
    #         original, updated_translated, "incorrect_answer")
    #     result = self.db.get_complementary_sentence(original)
    #     self.assertEqual(updated_translated, result)

    def test_insert_empty_strings(self):
        """Test inserting empty strings."""
        self.db.insert_sentence_pair("", "")
        result = self.db.fetch_all_sentence_pairs()
        self.assertEqual(
            0, len(result), "Should not insert empty sentence pairs")

    def test_insert_and_find_sentence_pair(self):
        """Test inserting a sentence pair and then finding it."""
        original_sentence = "This is a test sentence."
        translated_sentence = "これはテスト文です。"
        self.db.insert_sentence_pair(original_sentence, translated_sentence)

        result = self.db.find_sentence_pair(original_sentence)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], original_sentence)
        self.assertEqual(result[0][1], translated_sentence)

    def test_find_nonexistent_sentence_pair(self):
        """Test querying for a sentence pair that does not exist."""
        result = self.db.find_sentence_pair("Nonexistent sentence")
        self.assertEqual(result, [])

    def test_get_complementary_sentence(self):
        """Test retrieving the complementary sentence from a sentence pair."""
        original_sentence = "I wake up at nine."
        translated_sentence = "九点起床的。"
        self.db.insert_sentence_pair(original_sentence, translated_sentence)

        # Test getting the translated sentence using the original sentence
        result_translated = self.db.get_complementary_sentence(
            original_sentence)
        self.assertEqual(result_translated, translated_sentence)

        # Test getting the original sentence using the translated sentence
        result_original = self.db.get_complementary_sentence(
            translated_sentence)
        self.assertEqual(result_original, original_sentence)

        # Test with a sentence that does not exist
        result_nonexistent = self.db.get_complementary_sentence(
            "Nonexistent sentence")
        self.assertEqual(result_nonexistent, None)

    def test_get_exact_complementary_sentence(self):
        self.db.insert_sentence_pair("この工場は立ち入り禁止です。", "这个工厂禁止入内。")
        self.db.insert_sentence_pair("立ち入り禁止。", "禁止入内。")
        self.assertEqual(self.db.get_complementary_sentence("立ち入り禁止"), "禁止入内。")

    def test_get_complementary_sentence_with_punctuation_difference(self):
        """Test that sentences differing only by punctuation are considered a match."""
        self.db.insert_sentence_pair("Hello, world!", "你好，世界！")
        result = self.db.get_complementary_sentence("Hello, world")
        self.assertEqual(
            result, "你好，世界！", "Failed to match sentences differing only by punctuation.")

    def test_get_complementary_sentence_with_more_than_punctuation_difference(self):
        """Test that sentences differing by more than punctuation are not considered a match."""
        self.db.insert_sentence_pair("Good morning, everyone!", "大家早上好！")
        # Intentionally altering the query to differ by more than just punctuation
        result = self.db.get_complementary_sentence("Good morning")
        self.assertIsNone(
            result, "Incorrectly matched sentences differing by more than punctuation.")


if __name__ == '__main__':
    unittest.main()
