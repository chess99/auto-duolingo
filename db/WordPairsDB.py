import os
import sqlite3
from typing import List, Tuple


class WordPairsDB:
    def __init__(self, db_name: str = 'sentence_pairs.db'):
        """Initialize the database connection, storing the database file in the same data folder as SentencePairDB."""
        data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        if db_name == ":memory:":
            db_path = ":memory:"
        else:
            db_path = os.path.join(data_folder, db_name)
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def close(self):
        self.conn.close()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS word_pairs2 (
                    id INTEGER PRIMARY KEY,
                    word1 TEXT NOT NULL,
                    word2 TEXT NOT NULL,
                    UNIQUE(word1, word2)
                )
            ''')

    def insert_word_pair(self, words: Tuple[str, str]) -> int:
        # Sort the words to ensure (a, b) and (b, a) are treated as the same combination
        sorted_words = tuple(sorted(words))

        with self.conn:
            cursor = self.conn.execute('''
                INSERT OR IGNORE INTO word_pairs2 (word1, word2)
                VALUES (?, ?)
            ''', sorted_words)
            return cursor.lastrowid

    def query_related_words(self, word: str) -> List[str]:
        with self.conn:
            cursor = self.conn.execute('''
                SELECT word1, word2 FROM word_pairs2
                WHERE word1 = ? OR word2 = ?
            ''', (word, word))
            rows = cursor.fetchall()

        related_words = set()
        for row in rows:
            if row[0] != word:
                related_words.add(row[0])
            if row[1] != word:
                related_words.add(row[1])

        return list(related_words)

    def find_matches(self, original_words: List[str], options: List[str]):
        matches = {}
        for word in original_words:
            related_words = self.query_related_words(word)
            match_found = False
            for related_word in related_words:
                if related_word in options:
                    matches[word] = related_word
                    match_found = True
                    break
            if not match_found:
                matches[word] = None
        return matches
