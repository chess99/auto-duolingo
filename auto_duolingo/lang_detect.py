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


test_cases = [
    ("これはテストです", "Japanese"),
    ("カタカナ", "Japanese"),
    ("今日は学校に行きます", "Japanese"),
    ("スマホを充電する", "Japanese"),
    ("这是一个测试", "Chinese"),
    ("這是一個測試", "Chinese"),
    ("寿司は美味しいです", "Japanese"),
    ("寿司很好吃", "Chinese"),
    ("今日はいい天気ですね", "Japanese"),
    ("今天天气不错", "Chinese"),
    ("ナオキ", "Japanese"),
    ("王小明", "Chinese"),
    ("昔々あるところに", "Japanese"),
    ("故人西辞黄鹤楼", "Chinese"),
]


def run_test_cases():
    all_passed = True  # Flag to track if all tests pass
    for sentence, expected in test_cases:
        result = detect_language(sentence)
        if result != expected:
            all_passed = False  # Set flag to False if any test fails
            print(
                f"Sentence: '{sentence}' | Expected: {expected} | Detected: {result} | {'✅' if result == expected else '❌'}".encode('utf-8'))
    if all_passed:
        print("All test cases passed successfully.")


if __name__ == "__main__":
    run_test_cases()
