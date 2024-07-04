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

    # Sort by start position
    found_substrings.sort(key=lambda x: x[1])

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


if __name__ == "__main__":
    # Example usage
    substrings = ['を', '細かく', 'で', 'ください', '大豆', '刻ん', 'じゃがいも']
    sentence = "じゃがいもを細かく刻んでください。"
    sorted_substrings, unmatched = sort_substrings(sentence, substrings)
    print("Sorted Substrings:", sorted_substrings)
    print("Unmatched Part:", unmatched)
