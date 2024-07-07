
import os
import sqlite3
import uuid
from typing import List


class WordPairsDB:
    """
    A class to manage word pairs and their group associations in a SQLite database.

    Attributes:
        conn (sqlite3.Connection): Connection object to the SQLite database.
        cursor (sqlite3.Cursor): Cursor object used to execute SQL commands.

    Methods:
        __init__(db_name: str = ':memory:'): Initializes the database connection and creates the words table if it does not exist.
        insert_word_group(words: List[str]): Inserts a group of words into the database. If none of the words exist, all are inserted with a new group_id. If some words exist, new words are inserted with the existing group_id. If a word exists with a different group_id, it is updated.
        query_related_words(word: str): Queries the database for words related to the given word, i.e., words that share the same group_id.
        close(): Closes the database connection.
    """

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
        self.create_table_word_pairs()

    def __del__(self):
        self.close()

    def close(self):
        self.conn.close()

    def create_table_word_pairs(self):
        """Create the word_pairs table if it does not exist."""
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                group_id INTEGER
            );
        ''')
        self.conn.commit()

    def insert_word_group(self, words: List[str]) -> int:
        # Initialize the counter
        successful_inserts = 0

        # Check which words already exist in the database
        placeholders = ', '.join('?' for _ in words)
        self.cursor.execute(
            f'SELECT word, group_id FROM word_pairs WHERE word IN ({placeholders})', words)
        existing_words = {word: group_id for word,
                          group_id in self.cursor.fetchall()}

        if not existing_words:
            group_id = str(uuid.uuid4())
            for word in words:
                self.cursor.execute(
                    'INSERT INTO word_pairs (word, group_id) VALUES (?, ?)', (word, group_id))
                successful_inserts += 1  # Increment the counter
                print(f"Inserted '{word}' with group_id '{group_id}'.")
        else:
            # If some words exist, use the group_id of the first found word for all new words
            group_id = next(iter(existing_words.values()))
            for word in words:
                if word not in existing_words:
                    self.cursor.execute(
                        'INSERT INTO word_pairs (word, group_id) VALUES (?, ?)', (word, group_id))
                    successful_inserts += 1  # Increment the counter
                    print(f"Inserted '{word}' with group_id '{group_id}'.")
                else:
                    # If the word exists but has a different group_id, update it
                    if existing_words[word] != group_id:
                        self.cursor.execute(
                            'UPDATE word_pairs SET group_id = ? WHERE word = ?', (group_id, word))
                        successful_inserts += 1  # Increment the counter for updates as well
                        print(f"Updated '{word}' to group_id '{group_id}'.")

        self.conn.commit()
        return successful_inserts  # Return the count of successful inserts/updates

    def query_related_words(self, word: str) -> List[str]:
        self.cursor.execute(
            'SELECT group_id FROM word_pairs WHERE word = ?', (word,))
        result = self.cursor.fetchone()
        if result:
            group_id = result[0]
            self.cursor.execute(
                'SELECT word FROM word_pairs WHERE group_id = ?', (group_id,))
            return [row[0] for row in self.cursor.fetchall()]
        return []

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
