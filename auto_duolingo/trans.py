from typing import List

from zhipuai import ZhipuAI

from auto_duolingo.lang_detect import detect_language
from auto_duolingo.string_util import sort_substrings
from config import ZHIPUAI_API_KEY


def find_valid_translation(original_sentence: str, substrings: List[str], max_attempts: int = 3) -> List[str]:
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

    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)

    for _ in range(max_attempts):
        response = client.chat.completions.create(
            model="glm-4",
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
