import itertools

import spacy


def check_sentence(sentence):
    # Load the English model
    nlp = spacy.load('en_core_web_sm')

    # Parse the sentence
    doc = nlp(sentence)

    # Check if the sentence is grammatically correct
    # by checking if it has a root verb
    has_root_verb = any(token.dep_ == 'ROOT' and token.pos_ ==
                        'VERB' for token in doc)

    return has_root_verb


def find_sentence(words):
    for i in range(len(words), -1, -1):
        for permutation in itertools.permutations(words, i):
            if check_sentence(' '.join(list(permutation))):
                return list(permutation)
    return []


words = ['cat', 'the', 'sat', 'on', 'mat']
print(find_sentence(words))
