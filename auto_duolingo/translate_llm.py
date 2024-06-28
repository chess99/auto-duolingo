from typing import List

from zhipuai import ZhipuAI

from config import ZHIPUAI_API_KEY


def generate_sorted_sentence(original_sentence: str, words: List[str]) -> str:
    print("original_sentence: {}".format(original_sentence))
    print("words: {}".format(words))

    prompt = (
        "You are presented with a source sentence and a list of potential translation substrings. "
        "Your objective is to select specific substrings from the provided list and reorder them to construct a translation that accurately reflects the meaning of the original sentence. "
        "Additionally, consider if the selected combination of substrings can be translated back to the original sentence, ensuring the translation's accuracy.\n\n"
        "Guidelines:\n"
        "1. Choose and reorder the substrings to form a coherent translation of the source sentence.\n"
        "2. Output the reordered substrings as a single string, separated by the hash symbol (#). Do not include any additional explanations or symbols.\n"
        "3. Ensure that the final output contains only the selected substrings from the provided list. Do not include any content outside of the given options.\n"
        "4. Each item in the list can be used only once, except in cases where an item is repeated, in which case it can be used as many times as it appears in the list.\n"
        "5. Thoroughly consider various combinations and permutations of the substrings.\n"
        "6. Verify the correctness of your translation, ensuring it can be mapped back to the original sentence.\n"
        "Example of Output Format: [Substring A]#[Substring B]#[Substring C]...\n\n"
        f"List of substrings: {words}\n"
        f"Source sentence: \"{original_sentence}\""
    )

    translated_sentence = ""
    unmatched = words.copy()
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts and unmatched:
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

        sorted_substrings = translated_sentence.split('#')
        unmatched = [word for word in sorted_substrings if word not in words]

        if unmatched:
            unmatched_str = ', '.join(unmatched)
            prompt += f"\nPlease ensure not to use substrings outside of the provided list. The following substrings were not in the list: {unmatched_str}. Also, reconsider if the translation can accurately be mapped back to the original sentence."
        else:
            return sorted_substrings

    print("Error: Could not generate a valid translation with the provided substrings.")
    return []


def pick_semantically_matching_word(original_word: str, options: List[str]) -> str:
    print(f"Original word: {original_word}")
    print(f"Options: {options}")

    formatted_options = "\n".join([f"- {option}" for option in options])

    prompt = (
        f"Find the word that semantically matches or is closely related to '{original_word}' from the options listed below.\n"
        f"This may involve finding synonyms, related concepts, or the correct translation if applicable.\n"
        f"{formatted_options}\n"
        "Respond with only the selected option. Do not include any additional text or explanation."
    )

    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
    response = client.chat.completions.create(
        model="glm-4",
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.choices[0].message.content.strip()
    print(f"answer: {answer}")

    if answer in options:
        return answer
    else:
        return "Error: The selected option was not provided in the list."


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
