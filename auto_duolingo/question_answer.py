from typing import Dict, List, Tuple

from auto_duolingo.order import generate_sorted_sentence


def solve_translate_chi_jpn(sentence: str, words_with_bounds: List[Tuple[str, Dict[str, int]]]):
    sorted_boxes = generate_sorted_sentence(
        sentence, [word for word, _ in words_with_bounds])
    print(f"sorted_boxes: {sorted_boxes}")

    # Convert list of tuples to a list of dictionaries to keep track of processed words
    words_with_bounds_dicts = [{'word': word, 'bounds': bounds,
                                'processed': False} for word, bounds in words_with_bounds]

    # Collect bounds in the order they appear in sorted_boxes
    bounds_to_click = []
    for word in sorted_boxes:
        for word_dict in words_with_bounds_dicts:
            if word_dict['word'] == word and not word_dict['processed']:
                bounds_to_click.append(word_dict['bounds'])
                word_dict['processed'] = True  # Mark as processed
                break  # Move to the next word in sorted_boxes

    return bounds_to_click
