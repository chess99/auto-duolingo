def detect_language(sentence):
    # Japanese Hiragana & Katakana ranges
    hiragana_range = (ord(u'\u3040'), ord(u'\u309F'))
    katakana_range = (ord(u'\u30A0'), ord(u'\u30FF'))

    # Counters for Japanese characters
    hiragana_count = 0
    katakana_count = 0

    for char in sentence:
        # Count Hiragana
        if hiragana_range[0] <= ord(char) <= hiragana_range[1]:
            hiragana_count += 1
        # Count Katakana
        elif katakana_range[0] <= ord(char) <= katakana_range[1]:
            katakana_count += 1

    # Heuristic: If there's any Hiragana or Katakana, it's likely Japanese
    if hiragana_count > 0 or katakana_count > 0:
        return "Japanese"
    else:
        return "Chinese"
