import itertools
from translate import translate_sentence


# Function to find and order words based on the translation
def find_and_order_words(boxes, translated_sentence):
    # Split the translated sentence into words
    translated_words = translated_sentence.split()
    # Initialize an empty list to store the ordered words with their coordinates
    ordered_boxes = []
    # Iterate over each word in the translated sentence
    for word in translated_words:
        # Find the first box that matches the word and hasn't been used yet
        for box in boxes:
            if box[0] == word and box not in ordered_boxes:
                ordered_boxes.append(box)
                break
    return ordered_boxes

# Example usage
boxes = [
    ('を', (820, 1866, 130, 176)),
    ('細かく', (559, 1866, 244, 175)),
    ('で', (412, 1866, 130, 176)),
    ('ください', (129, 1866, 266, 176)),
    ('大豆', (714, 1674, 194, 175)),
    ('刻ん', (503, 1674, 194, 175)),
    ('じゃがいも', (170, 1674, 316, 176)),
    ('请把土豆细切。', (416, 582, 472, 162))
]

# Translate the original sentence (assuming the last item in boxes is the original sentence to be translated)
original_sentence = boxes[-1][0]
translated_sentence = translate_sentence(original_sentence)

# Find and order the words based on the translation
ordered_boxes = find_and_order_words(boxes[:-1], translated_sentence)  # Exclude the original sentence from the boxes

# Print the ordered boxes
print("Ordered Boxes:", ordered_boxes)