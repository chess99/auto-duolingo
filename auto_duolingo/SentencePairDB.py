import os
import sqlite3
from typing import List, Optional, Tuple


class SentencePairDB:
    def __init__(self, db_name='sentence_pairs.db'):
        """Initialize the database connection, storing the database file in a separate data folder."""
        data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        db_path = os.path.join(data_folder, db_name)
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        """Create the sentence_pairs table."""
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentence_pairs (
            id INTEGER PRIMARY KEY,
            original_sentence TEXT NOT NULL,
            translated_sentence TEXT NOT NULL
        )
        ''')
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_original ON sentence_pairs(original_sentence)')
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_translated ON sentence_pairs(translated_sentence)')
        self.conn.commit()

    def insert_sentence_pair(self, original_sentence, translated_sentence):
        """Insert a new sentence pair into the database if it doesn't already exist."""
        cursor = self.conn.cursor()
        # Check if the sentence pair already exists
        query = '''
        SELECT COUNT(*) 
        FROM sentence_pairs 
        WHERE original_sentence = ? OR translated_sentence = ?
        '''
        cursor.execute(query, (original_sentence, original_sentence))
        if cursor.fetchone()[0] == 0:  # If the count is 0, the pair does not exist
            cursor.execute('INSERT INTO sentence_pairs (original_sentence, translated_sentence) VALUES (?, ?)',
                           (original_sentence, translated_sentence))
            self.conn.commit()
        else:
            print("Sentence pair already exists in the database.")

    def insert_sentence_pair_2(self, original_sentence, translated_sentence):
        """Insert a new sentence pair into the database."""
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO sentence_pairs (original_sentence, translated_sentence) VALUES (?, ?)',
                       (original_sentence, translated_sentence))
        self.conn.commit()

    def find_sentence_pair(self, query_sentence: str) -> List[Tuple[str, str]]:
        """Find a sentence pair by searching both original and translated sentences."""
        cursor = self.conn.cursor()
        query = '''
        SELECT original_sentence, translated_sentence 
        FROM sentence_pairs 
        WHERE original_sentence LIKE ? OR translated_sentence LIKE ?
        '''
        cursor.execute(query, ('%' + query_sentence +
                       '%', '%' + query_sentence + '%'))
        results = cursor.fetchall()

        if results:
            return results
        else:
            return []

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

    def close(self):
        """Close the database connection."""
        self.conn.close()


# Example usage
if __name__ == "__main__":
    db = SentencePairDB()
    db.insert_sentence_pair("おとといは九時に起きました", "前天九点起床的")
    result = db.find_sentence_pair("おとといは九時に起きました")
    print(result)
    db.close()
