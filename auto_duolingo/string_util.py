import re


def sort_substrings(sentence, substrings):
    sentence = re.sub(r'[^\w\s]', '', sentence)

    found_substrings = []
    for sub in substrings:
        if sub == '':  # Skip empty strings to prevent infinite loop
            continue
        start = 0
        while True:
            start = sentence.find(sub, start)
            if start == -1:
                break
            found_substrings.append((sub, start))
            start += len(sub)  # Move past this substring

    # Sort by start position, then by length of the substring in descending order
    # To handle cases with partial overlaps correctly,
    # we need to adjust the logic to prioritize longer substrings when they start at the same position as shorter ones.
    found_substrings.sort(key=lambda x: (x[1], -len(x[0])))

    # Build the result list and the remaining sentence
    result_substrings = []
    last_end = 0
    for sub, start in found_substrings:
        if start >= last_end:
            result_substrings.append(sub)
            last_end = start + len(sub)

    # Reconstruct the unmatched part of the sentence
    unmatched = sentence
    for sub in result_substrings:
        unmatched = unmatched.replace(sub, '', 1)

    return result_substrings, unmatched
