from typing import List

from volcenginesdkarkruntime import Ark
from zhipuai import ZhipuAI

from config import ARK_API_KEY, ZHIPUAI_API_KEY


def generate_sorted_sentence(original_sentence: str, substrings: List[str]) -> List[str]:
    print(f"Original sentence: {original_sentence}")
    print(f"substrings: {substrings}")

    prompt = (
        "Task: \n"
        "From the given options, select and reorder the substrings to form a coherent translation "
        "of the source sentence according to the target language's linguistic conventions. You may not need to use all the provided substrings.\n"
        "Rules:\n"
        "1. Use ONLY the provided substrings. It's not mandatory to use all of them.\n"
        "2. Each substring can be used only as many times as it appears in the list.\n"
        "3. The translation should accurately reflect the original sentence's meaning, focusing on:\n"
        "   a. Words directly related to the original sentence's meaning.\n"
        "   b. Including necessary particles and modal words to maintain the sentence's integrity and tone.\n"
        "   c. Avoid selecting words that are unrelated to the original sentence's meaning.\n"
        "   d. The order of the selected substrings must follow the linguistic conventions of the target language.\n"
        "4. Output the result as a single string with substrings separated by '#'. Do not include any punctuation marks.\n"
        "5. Strictly follow the output format and do not include any additional content, explanations, or punctuation marks.\n"
        "6. Output format: substringA#substringB#substringC#...\n"
        "Reflection:\n"
        "   a. Can the selected substrings form a smooth and grammatically correct sentence in the target language?\n"
        "   b. Does the formed sentence accurately convey the same meaning as the original sentence?\n"
        "   c. Are there any selected substrings that do not belong to the provided list of options?\n"
        "   d. Does the formed sentence follows the linguistic conventions of the target language?\n"
        "Answer the following question based on the given instructions:\n"
        f"Original sentence: \"{original_sentence}\"\n"
        f"Substrings to use: {', '.join(substrings)}\n"
        "Return ONLY the hash-separated string as your response."
    )

    # print(f"prompt:\n{prompt}")

    # client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
    client = Ark(api_key=ARK_API_KEY)
    max_attempts = 3

    for attempt in range(max_attempts):
        response = client.chat.completions.create(
            # model="glm-4",
            model="ep-20240629142039-bt9sd",
            messages=[
                {"role": "system", "content": "You are a precise translation assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,  # Lower temperature for more focused outputs
            max_tokens=100,  # Adjust based on expected output length
        )

        response_content = response.choices[0].message.content.strip()
        print(f"Attempt {attempt + 1} result: {response_content}")

        sorted_options = response_content.rstrip('#').split('#')
        unmatched = [
            substring for substring in sorted_options if substring not in substrings]

        if unmatched:
            prompt += f"\n\nPrevious attempt: {response_content}\nError: Some substrings were not in the provided list or were used incorrectly. Please try again using ONLY the given substrings."
        else:
            return sorted_options

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


def sort_translations_by_original_order(original_words: List[str], options: List[str]) -> List[str]:
    print(f"original_words: {original_words}")
    print(f"options: {options}")

    prompt = (
        "Given a list of original words and a list of options containing semantically related words or translations in a mixed order, "
        "sort the options to match the semantic order of the original words. Return only the sorted list of options "
        "separated by a hash (#) symbol. Do not include the original words list, any explanations, or additional content. "
        "Here are the lists:\n\n"
        "Original words:\n" + "\n".join(f"- {word}" for word in original_words) +
        "\n\nOptions (mixed order):\n" +
        "\n".join(f"- {option}" for option in options)
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
    sorted_options = response_content.rstrip('#').split('#')
    return sorted_options


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
