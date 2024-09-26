import os
import unittest

from db.WordPairsDB import WordPairsDB


class TestWordPairsDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Construct the path to the test database file
        cls.current_dir = os.path.dirname(__file__)
        cls.data_folder = os.path.join(cls.current_dir, '..', 'data')
        cls.db_name = 'test_word_pairs.db'
        cls.db_path = os.path.join(cls.data_folder, cls.db_name)
        # Ensure the test database does not exist before starting tests
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        cls.db = WordPairsDB(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_create_table(self):
        # Check if the table is created successfully
        with self.db.conn:
            cursor = self.db.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='word_pairs2';")
            table_exists = cursor.fetchone()
            self.assertIsNotNone(table_exists)

    def test_insert_word_group(self):
        # Insert a word group and check if it is inserted correctly
        word_group = ('hello', 'world')
        row_id = self.db.insert_word_pair(word_group)
        self.assertGreater(row_id, 0)

        with self.db.conn:
            cursor = self.db.conn.execute(
                "SELECT word1, word2 FROM word_pairs2 WHERE word1=? AND word2=?", word_group)
            result = cursor.fetchone()
            self.assertEqual(result, word_group)

    def test_insert_word_group_sorted(self):
        # Insert a word group in reverse order and check if it is sorted and inserted correctly
        word_group = ('world', 'hello')
        row_id = self.db.insert_word_pair(word_group)
        self.assertGreater(row_id, 0)

        with self.db.conn:
            cursor = self.db.conn.execute(
                "SELECT word1, word2 FROM word_pairs2 WHERE word1=? AND word2=?", ('hello', 'world'))
            result = cursor.fetchone()
            self.assertEqual(result, ('hello', 'world'))

    def test_query_related_words(self):
        # Insert word groups and query related words
        self.db.insert_word_pair(('apple', 'banana'))
        self.db.insert_word_pair(('banana', 'cherry'))
        self.db.insert_word_pair(('cherry', 'date'))

        related_words = self.db.query_related_words('banana')
        self.assertIn('apple', related_words)
        self.assertIn('cherry', related_words)
        self.assertNotIn('date', related_words)

    def test_find_matches(self):
        # Insert word groups and find matches
        self.db.insert_word_pair(('cat', 'dog'))
        self.db.insert_word_pair(('elephant', 'crane'))
        self.db.insert_word_pair(('frog', 'elephant'))

        original_words = ['cat', 'elephant']
        options = ['dog', 'crane', 'giraffe']
        matches = self.db.find_matches(original_words, options)

        self.assertEqual(matches['cat'], 'dog')
        self.assertEqual(matches['elephant'], 'crane')


if __name__ == '__main__':
    unittest.main()
