import re
from string import punctuation as punc_en
from zhon.hanzi import punctuation as punc_cn

# 重要的关键字
key_word = {"不", "非"}
# 重要的同义词
synonym = {"癌": "恶性肿瘤",
           "III": "Ⅲ", "II": "Ⅱ", "I": "Ⅰ",
           "111": "Ⅲ", "11": "Ⅱ", "1": "Ⅰ", "2": "Ⅱ", "3": "Ⅲ", "4": "Ⅳ", "5": "Ⅴ",
           "Ⅰ": "1", "Ⅱ": "2", "Ⅲ": "3",
           }


def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif 65281 <= inside_code <= 65374:  # 全角字符（除空格）根据关系转化
            inside_code -= 65248
        rstring += chr(inside_code)
    return rstring


def filter_func(x):
    flag = True
    if x in punc_cn + punc_en:
        flag = False
    return flag


def seg_word(name):
    # 1. 将名称中的全角字符转成半角
    name = strQ2B(name)
    # 2. 将名称按照规定格式进行切分
    pattern = re.compile(r"([a-zA-Z0-9]*)")
    ps = pattern.split(name)
    return filter(filter_func, ps)


# print(list(filter(filter_func, re.split(r"([a-zA-Z]*)", s))))
if __name__ == '__main__':
    s = '胃腺癌并骨转移（TXNXM1;Ⅳ期）'
    print(s)
    print(list(seg_word(s)))
    tmp = ''.join((filter(filter_func, strQ2B(s))))
    print(tmp)
    pass
