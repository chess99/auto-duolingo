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


if __name__ == '__main__':
    unittest.main()
