import re
from typing import List

from volcenginesdkarkruntime import Ark
from zhipuai import ZhipuAI

from auto_duolingo.lang_detect import detect_language
from auto_duolingo.string_util import sort_substrings
from config import ARK_API_KEY, ZHIPUAI_API_KEY

LLM_IN_USE = "ark"  # "zhipuai" or "ark"


def _llm_get_client():
    if LLM_IN_USE == "zhipuai":
        return ZhipuAI(api_key=ZHIPUAI_API_KEY)
    elif LLM_IN_USE == "ark":
        return Ark(api_key=ARK_API_KEY)


def _llm_get_model_name():
    if LLM_IN_USE == "zhipuai":
        return "glm-4"
    elif LLM_IN_USE == "ark":
        return "ep-20240629142039-bt9sd"


def llm_sort_substrings(original_sentence: str, substrings: List[str], max_attempts=3) -> List[str]:
    original_language = detect_language(original_sentence)
    target_language = detect_language(' '.join(substrings))
    if original_language == "Japanese" and target_language == "Japanese":
        sorted_substrings, unmatched = sort_substrings(
            original_sentence, substrings)
        return sorted_substrings

    prompt = (
        "Task: \n"
        "First, identify the target language's specific variety from the context or the provided options. "
        "Then, from the given options, select and reorder the substrings to form a coherent translation "
        "of the source sentence according to the linguistic conventions of the identified target language variety. "
        "You may not need to use all the provided substrings.\n"
        "Rules:\n"
        "1. Use ONLY the provided substrings. It's not mandatory to use all of them.\n"
        "2. Each substring can be used only as many times as it appears in the list.\n"
        "3. The translation should accurately reflect the original sentence's meaning, focusing on:\n"
        "   a. Words directly related to the original sentence's meaning.\n"
        "   b. Including necessary particles and modal words to maintain the sentence's integrity and tone.\n"
        "   c. Avoid selecting words that are unrelated to the original sentence's meaning.\n"
        "   d. The order of the selected substrings must follow the linguistic conventions of the identified target language variety.\n"
        "4. Output the result as a single string with substrings separated by '#'. Do not include any punctuation marks.\n"
        "5. Strictly follow the output format and do not include any additional content, explanations, or punctuation marks.\n"
        "6. Output format: substringA#substringB#substringC#...\n"
        "Reflection:\n"
        "   a. Can the selected substrings form a smooth and grammatically correct sentence in the target language?\n"
        "   b. Does the formed sentence accurately convey the same meaning as the original sentence?\n"
        "   c. Are there any selected substrings that do not belong to the provided list of options?\n"
        "   d. Does the formed sentence follow the linguistic conventions of the identified target language variety?\n"
        "Answer the following question based on the given instructions:\n"
        f"Original sentence: \"{original_sentence}\"\n"
        f"Substrings to use: {', '.join(substrings)}\n"
        "Return ONLY the hash-separated string as your response."
    )

    client = _llm_get_client()
    for attempt in range(max_attempts):
        response = client.chat.completions.create(
            model=_llm_get_model_name(),
            messages=[
                {"role": "system", "content": "You are a precise translation assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,  # Lower temperature for more focused outputs
            max_tokens=100,  # Adjust based on expected output length
        )

        response_content = response.choices[0].message.content.strip()
        print(f"Attempt {attempt + 1} result: {response_content}")

        sorted_options = [re.sub(r'[^\w\s]', '', option.strip())
                          for option in response_content.rstrip('#').split('#')]
        sorted_options = list(filter(None, sorted_options))
        unmatched = [
            substring for substring in sorted_options if substring not in substrings]

        if unmatched:
            print("unmatched: ", unmatched)
            prompt += f"\n\nPrevious attempt: {response_content}\nError: Some substrings were not in the provided list or were used incorrectly. Please try again using ONLY the given substrings."
        else:
            return sorted_options

    print("Error: Could not generate a valid translation with the provided substrings.")
    return []

def llm_sort_substrings_2(original_sentence: str, substrings: List[str], max_attempts: int = 3) -> List[str]:
    original_language = detect_language(original_sentence)
    target_language = detect_language(' '.join(substrings))
    if original_language == "Japanese" and target_language == "Japanese":
        sorted_substrings, unmatched = sort_substrings(
            original_sentence, substrings)
        return sorted_substrings

    print(f"target_language: {target_language}")

    prompt = (
        f"Translate the following sentence into {target_language} accurately, "
        f"ensuring the meaning of the translation aligns closely with the original sentence: \"{original_sentence}\". "
        f"Use ONLY the provided substrings: {', '.join(substrings)}. "
        f"Be mindful that not all provided substrings may be relevant. Prioritize the translation's accuracy and fidelity to the original meaning, "
        f"but do not use words outside the provided options. "
        f"If a substring doesn't fit or compromises the translation's accuracy or meaning, reconsider its use. "
        f"Ensure the translation conveys the same meaning as the original sentence without using words outside the provided substrings. "
        f"Return ONLY the translation string as your response."
    )

    client = _llm_get_client()
    for _ in range(max_attempts):
        response = client.chat.completions.create(
            model=_llm_get_model_name(),
            messages=[
                {"role": "system", "content": "You are a translation assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=100,
        )
        translation = response.choices[0].message.content.strip()
        print(f"Translation attempt: {translation}")
        sorted_substrings, unmatched = sort_substrings(translation, substrings)
        if not unmatched:  # If all substrings are matched, return this translation
            return sorted_substrings

    print("No valid translation found after all attempts.")
    return []



def llm_pick_semantically_matching_word(original_word: str, options: List[str]) -> str:
    print(f"Original word: {original_word}")
    print(f"Options: {options}")

    formatted_options = "\n".join([f"- {option}" for option in options])

    prompt = (
        f"Find the word that semantically matches or is closely related to '{original_word}' from the options listed below.\n"
        f"This may involve finding synonyms, related concepts, or the correct translation if applicable.\n"
        f"{formatted_options}\n"
        "Respond with only the selected option. Do not include any additional text or explanation."
    )

    client = _llm_get_client()
    response = client.chat.completions.create(
        model=_llm_get_model_name(),
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    answer = response.choices[0].message.content.strip()
    print(f"answer: {answer}")

    if answer in options:
        return answer
    else:
        print("Error: The selected option was not provided in the list.")
        return None


def llm_pick_corresponding_pronunciation(original_word: str, options: List[str]) -> str:
    print(f"Original word: {original_word}")
    print(f"Options: {options}")

    formatted_options = "\n".join([f"- {option}" for option in options])

    prompt = (
        f"Given the word '{original_word}', select the option that best matches its pronunciation. "
        "The options provided are in various phonetic representations such as Pinyin for Chinese, "
        "Romaji for Japanese, or Hiragana. This task focuses on matching the pronunciation rather than the meaning. "
        "In cases where the original word may correspond to multiple pronunciations in the options, "
        "consider the meaning of the original word to choose the most appropriate pronunciation.\n"
        f"{formatted_options}\n"
        "Please respond with only the selected option. Do not include any additional text or explanation."
    )

    client = _llm_get_client()
    response = client.chat.completions.create(
        model=_llm_get_model_name(),
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.choices[0].message.content.strip()
    print(f"answer: {answer}")

    if answer in options:
        return answer
    else:
        print("Error: The selected option was not provided in the list.")
        return None


def llm_sort_translations_by_original_order(original_words: List[str], options: List[str]) -> List[str]:
    print(f"original_words: {original_words}")
    print(f"options: {options}")

    prompt = (
        "Given a list of original words and a list of options containing semantically related words "
        "or translations in a mixed order, your task is to think through each original word one at a time, "
        "and sort the options to match the semantic order of the original words. "
        "For each original word, identify the corresponding option that best matches or translates it. "
        "After considering all original words and finding their matches, "
        "return only the sorted list of options separated by a hash (#) symbol. "
        "Do not include the original words list, any explanations, or additional content.\n\n"
        "Here are the lists:\n\n"
        f"Original words: {', '.join(original_words)}\n"
        f"Options (mixed order): {', '.join(options)}\n"
        "Output format: wordA#wordB#wordC#...\n"
        "return ONLY the hash-separated string as your response."
    )

    client = _llm_get_client()
    response = client.chat.completions.create(
        model=_llm_get_model_name(),
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
    sorted_sentence = llm_sort_substrings(original_sentence, words)
    print(sorted_sentence)
    print(type(sorted_sentence))
