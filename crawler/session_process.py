import json
import os

from db.SentencePairDB import SentencePairDB
from db.WordPairsDB import WordPairsDB


def process_assist(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]
    WordPairsDB().insert_word_group([prompt, correct_choice])
    return prompt, correct_choice


def process_listenTap(item):
    metadata = item['metadata']
    translation_data = {
        'sentence': metadata.get('text'),
        'translation': metadata.get('solution_translation'),
        'tokens': metadata.get('tokens'),
        'learning_language': metadata.get('learning_language'),
        'from_language': metadata.get('from_language')
    }
    SentencePairDB().insert_sentence_pair(
        translation_data['sentence'], translation_data['translation'])
    return translation_data


def process_characterMatch(item):
    pairs = item.get('pairs', [])
    extracted_tokens = []
    for pair in pairs:
        from_token = pair.get('character')
        learning_token = pair.get('transliteration')
        extracted_tokens.append((from_token, learning_token))
        WordPairsDB().insert_word_group([from_token, learning_token])
    return extracted_tokens


def process_match(item):
    pairs = item.get('pairs', [])
    extracted_tokens = []
    for pair in pairs:
        from_token = pair.get('fromToken')
        learning_token = pair.get('learningToken')
        extracted_tokens.append((from_token, learning_token))
        WordPairsDB().insert_word_group([from_token, learning_token])
    return extracted_tokens


def process_characterIntro(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]
    WordPairsDB().insert_word_group([prompt, correct_choice])
    return prompt, correct_choice


def process_translate(item):
    metadata = item['metadata']
    translation_data = {
        'sentence': metadata.get('sentence'),
        'translation': metadata.get('translation'),
        'tokens': metadata.get('tokens'),
        'learning_language': metadata.get('learning_language'),
        'from_language': metadata.get('from_language')
    }
    SentencePairDB().insert_sentence_pair(
        translation_data['sentence'], translation_data['translation'])
    return translation_data


def process_characterSelect(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]['character']
    WordPairsDB().insert_word_group([prompt, correct_choice])
    return prompt, correct_choice


def process_select(item):
    prompt = item['prompt']
    correct_choice = item['choices'][item['correctIndex']]['phrase']
    WordPairsDB().insert_word_group([prompt, correct_choice])
    return prompt, correct_choice


def process_not_implemented(item):
    print(f"Function not implemented for type: {item['type']}")
    return None


def process_challenge_skipping(item):
    pass


# Dispatch dictionary
dispatch_map = {
    'characterSelect': process_characterSelect,
    'select': process_select,
    'assist': process_assist,
    'listenTap': process_listenTap,
    'characterMatch': process_characterMatch,
    'match': process_match,
    'characterIntro': process_characterIntro,
    'translate': process_translate,
    'selectPronunciation': process_challenge_skipping,
}


def process_challenge(item):
    # Assuming 'type' key exists in item
    type_name = item['type']
    if type_name in dispatch_map:
        result = dispatch_map[type_name](item)
        print(f"{type_name}: {result}")
    else:
        print(f"No process function for type: {type_name}")


def load_and_process_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        challenges = data.get('challenges', [])

        for challenge in challenges:
            process_challenge(challenge)


def process_all_sessions(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}")
                load_and_process_data(file_path)


if __name__ == "__main__":
    sessions_directory = ".temp/sessions/"
    process_all_sessions(sessions_directory)
