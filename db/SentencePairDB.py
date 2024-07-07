import os
import re
import sqlite3
from typing import List, Optional, Tuple

# pylint: disable=no-name-in-module
from jellyfish import levenshtein_distance


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

    def __del__(self):
        self.close()

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

    def insert_sentence_pair(self, original_sentence: str, translated_sentence: str, source: str = "") -> int:
        """Insert a new sentence pair into the database if it doesn't already exist, or update if source is 'incorrect_source'. Returns the number of successful inserts/updates."""

        # Prevent insertion of empty sentence pairs
        if not original_sentence.strip() or not translated_sentence.strip():
            print("Cannot insert empty sentence pairs.")
            return 0

        cursor = self.conn.cursor()
        success_count = 0

        # Check if the sentence pair already exists
        query = '''
        SELECT id 
        FROM sentence_pairs 
        WHERE original_sentence = ? AND translated_sentence = ?
        '''
        cursor.execute(query, (original_sentence, translated_sentence))
        result = cursor.fetchone()

        if result is None:  # If the pair does not exist, insert it
            cursor.execute('INSERT INTO sentence_pairs (original_sentence, translated_sentence, source) VALUES (?, ?, ?)',
                           (original_sentence, translated_sentence, source))
            success_count = 1
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
                success_count = 1
            else:
                # print("Sentence pair already exists in the database.")
                pass

        self.conn.commit()
        return success_count

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
        results = self.find_sentence_pair(query_sentence)
        print(f"results: {results}")
        if not results:
            return None

        lowest_distance = float('inf')
        # Holds the best matching original and translated sentences
        best_match_pair = (None, None)

        for original, translated in results:
            # Calculate distance from the query to both the original and translated sentences
            distance_original = levenshtein_distance(query_sentence, original)
            distance_translated = levenshtein_distance(
                query_sentence, translated)

            # Update if a closer match is found
            if distance_original < lowest_distance:
                lowest_distance = distance_original
                best_match_pair = (original, translated)
            if distance_translated < lowest_distance:
                lowest_distance = distance_translated
                best_match_pair = (translated, original)

        # Remove punctuation from both sentences for comparison

        def remove_punctuation(s: str) -> str:
            return re.sub(r'[^\w\s]', '', s)

        query_no_punct = remove_punctuation(query_sentence)
        best_match_no_punct = remove_punctuation(best_match_pair[0])
        print(f"query_no_punct: {query_no_punct}")
        print(f"best_match_no_punct: {best_match_no_punct}")

        # Check if the difference is only in punctuation
        if query_no_punct != best_match_no_punct:
            return None

        return best_match_pair[1]

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
