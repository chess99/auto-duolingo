import ast
import re
from typing import List

from zhipuai import ZhipuAI

from auto_duolingo.string_match import sort_substrings
from config import ZHIPUAI_API_KEY


def extract_bracketed_content(input_str: str) -> List[str]:
    # Attempt to match content within square brackets using regex
    match = re.search(r'\[(.*?)\]', input_str)
    if match:
        # Get the matched content without the brackets
        content = match.group(1)
        try:
            # Safely parse the string using ast.literal_eval
            parsed_content = ast.literal_eval(content)
            return parsed_content
        except Exception as e:
            # Print error and return an empty string if parsing fails
            print(f"Error parsing content: {e}")
            return []
    else:
        # Return an empty string if no content is matched
        return []


def generate_sorted_sentence_2(words: List[str], original_sentence: str) -> List[str]:
    print("Words: {}".format(words))
    print("Original Sentence: {}".format(original_sentence))

    prompt = (
        f"请根据原句的含义，从给定的词汇列表中选择一些词汇并重新排序, 使排序后的词汇能构造一个与原句意义相符的句子, 并且保证语法正确。"
        f"请以Python列表格式直接提供最终的、经过筛选和排列的词汇列表。无需展示选择过程。"
        f"\n"
        f"词汇列表： {words}\n"
        f"原句： \"{original_sentence}\""
    )

    # 使用ZhipuAI
    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)  # Use the imported API key
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    # Access the content attribute directly
    sorted_sentence_content = response.choices[0].message.content
    print("Sorted Sentence Content: {}".format(sorted_sentence_content))

    # Use extract_bracketed_content to safely parse the sorted sentence list
    sorted_sentence_list = extract_bracketed_content(sorted_sentence_content)
    return sorted_sentence_list


def generate_sorted_sentence(words: List[str], original_sentence: str) -> List[str]:
    print("Words: {}".format(words))
    print("Original Sentence: {}".format(original_sentence))

    prompt = (
        f"请将原句翻译成日语, 翻译结果只能使用词汇列表中有的词汇, 且每个词汇只能使用一次。"
        f"请直接返回翻译后的语句, 不要添加多余的说明和符号。"
        f"\n"
        f"词汇列表： {words}\n"
        f"原句： \"{original_sentence}\""
    )

    # 使用ZhipuAI
    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)  # Use the imported API key
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    # Access the content attribute directly
    translated_sentence = response.choices[0].message.content
    print("translated_sentence: {}".format(translated_sentence))

    # 对比translated_sentence, 从words中选出所需词汇并排序
    sorted_substrings, unmatched = sort_substrings(translated_sentence, words)
    return sorted_substrings


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
    sorted_sentence = generate_sorted_sentence(words, original_sentence)
    print(sorted_sentence)
    print(type(sorted_sentence))
