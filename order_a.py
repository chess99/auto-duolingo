import itertools
import spacy
from sentence_transformers import SentenceTransformer, util

# Load the GiNZA model for Japanese
nlp = spacy.load('ja_core_news_sm')

# Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

def check_sentence(sentence):
    doc = nlp(sentence)
    # Check if the sentence ends with a verb
    ends_with_verb = doc[-1].pos_ == 'VERB'
    
    # Check if there's at least one particle in the sentence
    has_particle = any(token.pos_ == 'ADP' for token in doc)
    
    return ends_with_verb and has_particle


def is_semantically_similar(sentence, translation, threshold=0.5):
    # Convert sentences to embeddings
    sentence_embedding = model.encode(sentence, convert_to_tensor=True)
    translation_embedding = model.encode(translation, convert_to_tensor=True)
    
    # Compute cosine similarity
    cosine_similarity = util.pytorch_cos_sim(sentence_embedding, translation_embedding)
    
    # Check if similarity is above a certain threshold
    return cosine_similarity.item() > threshold


def find_sentence(boxes, translation):
    # Extract texts from the relevant boxes (excluding the translation)
    words = [box[0] for box in boxes[:-1]]
    
    # Try permutations of the words to find a sentence semantically similar to the translation
    for i in range(len(words), 0, -1):  # Start from the full length to 1
        for permutation in itertools.permutations(words, i):
            sentence = ' '.join(permutation)
            if check_sentence(sentence) and is_semantically_similar(sentence, translation):
                return permutation  # Return the first correct permutation
    return []

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

# Extract the translation from the last item of the boxes list
translation = boxes[-1][0]

# Find the correct order of words that matches the translation
correct_order = find_sentence(boxes, translation)
print("Correct Order:", correct_order)