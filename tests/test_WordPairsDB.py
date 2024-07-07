import unittest

from db.WordPairsDB import WordPairsDB


class TestWordPairsDB(unittest.TestCase):
    def setUp(self):
        # Create a new database in memory for each test
        self.db = WordPairsDB(db_name=":memory:")

    def tearDown(self):
        # Close the database after each test
        self.db.close()

    def test_insert_and_query_single_pair(self):
        self.db.insert_word_group(['word1', 'word2'])
        result = self.db.query_related_words('word1')
        self.assertIn('word1', result)
        self.assertIn('word2', result)
        self.assertEqual(len(result), 2)

    def test_insert_and_query_multiple_pairs(self):
        self.db.insert_word_group(['word1', 'word2'])
        self.db.insert_word_group(['word1', 'word3'])
        self.db.insert_word_group(['word3', 'word4'])
        self.db.insert_word_group(['word4', 'word5', 'word6'])
        result = self.db.query_related_words('word1')
        expected_words = ['word1', 'word2', 'word3', 'word4', 'word5', 'word6']
        self.assertEqual(len(result), len(expected_words))
        for word in expected_words:
            self.assertIn(word, result)

    def test_query_nonexistent_word(self):
        result = self.db.query_related_words('nonexistent')
        self.assertEqual(len(result), 0)

    def test_insert_existing_word(self):
        self.db.insert_word_group(['word1', 'word2'])
        self.db.insert_word_group(['word2', 'word3'])  # word2 already exists
        result = self.db.query_related_words('word1')
        self.assertIn('word3', result)
        self.assertEqual(len(result), 3)

    def test_insert_with_existing_and_new_word(self):
        self.db.insert_word_group(['word1', 'word2'])
        self.db.insert_word_group(['word2', 'word3'])
        # newword is new, word3 exists
        self.db.insert_word_group(['word3', 'newword'])
        result = self.db.query_related_words('word1')
        self.assertIn('newword', result)
        self.assertEqual(len(result), 4)

    def test_find_matches_multiple_words(self):
        # Setup: Insert word groups into the database
        self.db.insert_word_group(['apple', 'banana'])
        self.db.insert_word_group(['banana', 'cantaloupe'])
        self.db.insert_word_group(['date', 'elderberry'])

        # Define options
        options = ['apple', 'banana', 'cantaloupe',  'elderberry']

        # Action: Find matches for multiple words with options
        matches = self.db.find_matches(['banana', 'date'], options)

        # Assertion: Check if the matches dictionary is correct
        expected_matches = {'banana': 'apple', 'date': 'elderberry'}
        self.assertEqual(matches, expected_matches)

    def test_find_matches_with_nonexistent_word(self):
        # Setup: Insert word groups into the database
        self.db.insert_word_group(['apple', 'banana'])

        # Define options
        options = ['apple', 'banana']

        # Action: Find matches including a nonexistent word with options
        matches = self.db.find_matches(['banana', 'nonexistent'], options)

        # Assertion: Check if the matches dictionary is correct, including handling of the nonexistent word
        expected_matches = {'banana': 'apple', 'nonexistent': None}
        self.assertEqual(matches, expected_matches)


if __name__ == '__main__':
    unittest.main()
