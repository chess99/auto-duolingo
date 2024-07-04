import os
import sqlite3
from typing import List, Optional, Tuple


class SentencePairDB:
    def __init__(self, db_name='sentence_pairs.db'):
        """Initialize the database connection, storing the database file in a separate data folder."""
        data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        if db_name == ":memory:":
            db_path = ":memory:"
        else:
            db_path = os.path.join(data_folder, db_name)
        self.conn = sqlite3.connect(db_path)
        self.create_table_sentence_pairs()

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def create_table_sentence_pairs(self):
        """Create the sentence_pairs table."""
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentence_pairs (
            id INTEGER PRIMARY KEY,
            original_sentence TEXT NOT NULL,
            translated_sentence TEXT NOT NULL,
            source TEXT
        )
        ''')
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_original ON sentence_pairs(original_sentence)')
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_translated ON sentence_pairs(translated_sentence)')
        self.conn.commit()

    def insert_sentence_pair(self, original_sentence: str, translated_sentence: str, source: str = "") -> None:
        """Insert a new sentence pair into the database if it doesn't already exist, or update if source is 'incorrect_source'."""

        # Prevent insertion of empty sentence pairs
        if not original_sentence.strip() or not translated_sentence.strip():
            print("Cannot insert empty sentence pairs.")
            return

        cursor = self.conn.cursor()

        # Check if the sentence pair already exists
        query = '''
        SELECT id 
        FROM sentence_pairs 
        WHERE original_sentence = ? OR translated_sentence = ?
        '''
        cursor.execute(query, (original_sentence, translated_sentence))
        result = cursor.fetchone()

        if result is None:  # If the pair does not exist, insert it
            cursor.execute('INSERT INTO sentence_pairs (original_sentence, translated_sentence, source) VALUES (?, ?, ?)',
                           (original_sentence, translated_sentence, source))
        else:
            # If the pair exists and source is 'incorrect_answer', update the entry
            if source == 'incorrect_answer':
                update_query = '''
                UPDATE sentence_pairs
                SET original_sentence = ?, translated_sentence = ?, source = ?
                WHERE id = ?
                '''
                cursor.execute(update_query, (original_sentence,
                               translated_sentence, source, result[0]))
            else:
                print("Sentence pair already exists in the database.")

        self.conn.commit()

    def find_sentence_pair(self, query_sentence: str) -> List[Tuple[str, str]]:
        """Find a sentence pair by searching both original and translated sentences."""
        cursor = self.conn.cursor()
        query = '''
        SELECT original_sentence, translated_sentence
        FROM sentence_pairs 
        WHERE original_sentence LIKE ? OR translated_sentence LIKE ?
        '''
        search_term = f'%{query_sentence}%'
        cursor.execute(query, (search_term, search_term))
        return cursor.fetchall()

    def get_complementary_sentence(self, query_sentence: str) -> Optional[str]:
        """Get the sentence from the pair that is not the query_sentence."""
        results = self.find_sentence_pair(query_sentence)
        if not results:  # Check if results is an empty list
            return None  # Return None if no matching sentence pair is found

        for original, translated in results:
            if query_sentence in original:
                return translated
            elif query_sentence in translated:
                return original

        return None

    def fetch_all_sentence_pairs(self) -> List[Tuple[str, str, str, int]]:
        """Fetch all sentence pairs from the database."""
        cursor = self.conn.cursor()
        query = '''
        SELECT original_sentence, translated_sentence, source, id
        FROM sentence_pairs
        '''
        cursor.execute(query)
        return cursor.fetchall()


# Example usage
if __name__ == "__main__":
    db = SentencePairDB()
    db.insert_sentence_pair("おとといは九時に起きました", "前天九点起床的")
    result = db.find_sentence_pair("おとといは九時に起きました")
    print(result)
    db.close()
