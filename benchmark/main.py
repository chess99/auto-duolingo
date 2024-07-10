# get_cached_sentence_pairs()
# 每一项都是一个字典，包含三个键：sentence, translation, tokens
# 其中，sentence是原句，translation是翻译, tokens 是翻译句子的分词, wrongTokens 是干扰项
# { "sentence": "日ようびは忙しいです。", "translation": "星期天很忙。", "tokens": [ "日", "よう", "び", "は", "忙しい", "です" ] }
#
# llm_generate_sorted_sentence(original_sentence: str, substrings: List[str], max_attempts=3) -> List[str]
# 第一个参数是原句，对应get_cached_sentence_pairs()的sentence
# 第二个参数是翻译句子的分词的选项，tokens 与 wrongTokens 合并然后乱序后的结果
# 第三个参数是最大尝试次数
# 返回结果是一个列表，当与 tokens 一致时，表示函数成功，否则表示失败
#
# find_valid_translation(original_sentence: str,  substrings: List[str], max_attempts: int = 3) -> List[str]
# 和 llm_generate_sorted_sentence 功能完全一致
# 写一个 benchmark 函数，测试这两个函数的准确率
# 从 get_cached_sentence_pairs() 的结果中随机取出 20 个，然后分别调用这两个函数，max_attempts 都使用 1, 统计准确率
import random

from auto_duolingo.trans import find_valid_translation
from auto_duolingo.translate_llm import llm_generate_sorted_sentence
from crawler.persist import get_cached_sentence_pairs


def randomize_tokens(tokens, wrongTokens):
    # Combine tokens and wrongTokens, then shuffle
    all_tokens = tokens + wrongTokens
    random.shuffle(all_tokens)
    return all_tokens


def benchmark(sample_count=3, llm_attempts=1):

    sentence_pairs = random.sample(get_cached_sentence_pairs(), sample_count)
    llm_v1_success_count = 0
    llm_v2_success_count = 0

    for pair in sentence_pairs:

        substrings = randomize_tokens(pair["tokens"], pair["wrongTokens"])

        print(f'sentence: {pair["sentence"]}')
        print(f'tokens: {pair["tokens"]}')
        print(f"substrings: {substrings}")

        llm_v1_result = llm_generate_sorted_sentence(
            pair["sentence"], substrings, llm_attempts)
        print(f"llm_v1_result: {llm_v1_result}")
        if llm_v1_result == pair["tokens"]:
            llm_v1_success_count += 1

        llm_v2_result = find_valid_translation(
            pair["sentence"], substrings, llm_attempts)
        print(f"llm_v2_result: {llm_v2_result}")
        if llm_v2_result == pair["tokens"]:
            llm_v2_success_count += 1

    print(f"LLM-v1 Accuracy: {llm_v1_success_count / sample_count:.2%}")
    print(f"LLM-v2 Accuracy: {llm_v2_success_count / sample_count:.2%}")


if __name__ == "__main__":
    benchmark(sample_count=1)
