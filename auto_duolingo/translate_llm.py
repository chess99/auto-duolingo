import re
from typing import List

from zhipuai import ZhipuAI

from auto_duolingo.string_match import sort_substrings
from config import ZHIPUAI_API_KEY


def generate_sorted_sentence(original_sentence: str, words: List[str]) -> List[str]:
    print("original_sentence: {}".format(original_sentence))
    print("words: {}".format(words))

    prompt = (
        f"请将下列句子翻译。"
        f"翻译中仅使用以下选项列表中的词汇，并且每个选项仅使用一次。"
        f"不要使用选项列表之外的词汇。"
        f"根据选项列表自动判断目标翻译语言。"
        f"确保翻译的句子意思与原句相符。"
        f"请直接返回翻译后的语句, 不要添加多余的说明和符号。"
        f"\n"
        f"选项列表： {words}\n"
        f"原句： \"{original_sentence}\""
    )

    # Initialize variables for loop
    translated_sentence = ""
    unmatched = None
    attempts = 0
    max_attempts = 3  # Prevent infinite loops

    while attempts < max_attempts and (unmatched is None or unmatched.strip()):
        attempts += 1
        client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
        response = client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )

        translated_sentence = response.choices[0].message.content
        print("translated_sentence: {}".format(translated_sentence))

        sorted_substrings, unmatched = sort_substrings(
            translated_sentence, words)

        # Remove punctuation from unmatched
        unmatched = re.sub(r'[^\w\s]', '', unmatched)
        print(f"unmatched: {unmatched}")

        if unmatched.strip():
            # Update prompt with unmatched content information
            prompt += f"\n注意翻译时不要使用以下未在选项列表中的词汇：{unmatched}"

    return sorted_substrings


def pick_translation_for_word(original_word: str, options: List[str]) -> str:
    print(f"original_word: {original_word}")
    print(f"options: {options}")

    # Formatting options for clarity
    formatted_options = "\n".join([f"- {option}" for option in options])

    prompt = (
        f"Given the word '{original_word}', select the correct translation from the following options:\n"
        f"{formatted_options}\n"
        f"Type the correct option exactly as it appears above."
    )

    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    answer = response.choices[0].message.content.strip()
    print(f"answer: {answer}")
    return answer


def sort_translations_by_original_order(original_words: List[str], translations: List[str]) -> List[str]:
    print(f"original_words: {original_words}")
    print(f"translations: {translations}")

    prompt = (
        "Given two lists of words where the first list contains original words and the second list contains their translations "
        "in a mixed order, sort the translations to match the order of the original words. Return only the sorted list of translations "
        "separated by a hash (#) symbol. Do not include the original words list, any explanations, or additional content. "
        "Here are the lists:\n\n"
        "Original words:\n" + "\n".join(f"- {word}" for word in original_words) +
        "\n\nTranslations (mixed order):\n" +
        "\n".join(f"- {translation}" for translation in translations)
    )

    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    response_content = response.choices[0].message.content.strip()
    print(f"response_content: {response_content}")

    # Remove the trailing hash (if any) before splitting
    sorted_translations = response_content.rstrip('#').split('#')
    return sorted_translations


if __name__ == "__main__":
    # 准备数据
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
    original_sentence = boxes[-1][0]  # 翻译原句
    # Extract words, excluding the original sentence
    words = [word for word, _ in boxes[:-1]]

    # 调用函数并打印结果
    sorted_sentence = generate_sorted_sentence(original_sentence, words)
    print(sorted_sentence)
    print(type(sorted_sentence))
