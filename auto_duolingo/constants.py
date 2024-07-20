from enum import Enum


class QuestionType(Enum):
    UNKNOWN = 0
    # "翻译这句话"
    TRANSLATE_SENTENCE = 2
    # "请选择正确的翻译", 一个单词, 三个翻译选项选择一个
    CHOOSE_CORRECT_TRANSLATION = 3
    # "选择对应的图片", 一个单词, 四个图片选项选择一个
    CHOOSE_CORRECT_PICTURE = 4
    # "选择配对", 左边五个原词, 从右边五个词中选择对应的翻译
    CHOOSE_MATCHING_PAIR = 5
    # "这个怎么读？"
    HOW_TO_PRONOUNCE = 6
    # "选择 “xxxx” 对应的字符", 一个平假名单词, 四个汉字选项选择一个
    CHOOSE_CORRECT_CHARACTER = 7