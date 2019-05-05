import os
import time
import math
import heapq
import pickle
import simhash
import Levenshtein
from model.sub_module import strQ2B
from model.sub_module import synonym
from model.sub_module import seg_word
from model.sub_module import key_word
from model.sub_module import filter_func


def get_simhash_dis(str1, str2):
    """计算两个文本之间的simhash相似度"""
    simhash_str1 = simhash.Simhash(str1)
    simhash_str2 = simhash.Simhash(str2)
    dis_simhash = 1 - simhash_str1.distance(simhash_str2) / 64
    dis_ratio = Levenshtein.ratio(str1, str2)
    dis_jaro = Levenshtein.jaro(str1, str2)
    res = (dis_simhash + dis_ratio + dis_jaro) / 3
    return res


def load_words(filepath="../data/data_result/standard_icd10.pkl"):
    # 获取标疾病名称表; 键: 疾病名称; 值: icd
    with open(filepath, mode="rb") as f:
        words = pickle.load(f)
    return words


def load_entity(words):
    """获取标准名称中的所有实体"""
    entity = set()
    for item in words.keys():
        entity |= set(seg_word(item))
    return entity


def load_reverse(entity, words, filepath="./tmp/reverse.pkl"):
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
    else:
        t_s = time.time()
        ans = {}
        for item in entity:
            tmp = []
            for ws in words:
                if item in ws:
                    tmp.append(ws)
            if len(tmp) > 0:
                ans[item] = tmp
        with open(filepath, 'wb') as f:
            pickle.dump(ans, f)
        t_e = time.time()
        print("构造逆序字典用时：{}秒。".format(t_e - t_s))
        return ans


def calc_tfidf(seg, reverse):
    """计算分词之后对应的tfidf值"""
    tfidf = dict()
    for item in seg:
        w = 1
        if not reverse.get(item):
            tfidf[item] = 0
        else:
            cnt = len(reverse.get(item))
            if cnt and cnt > 0:
                tfidf[item] = w / math.log(cnt + 1, 2)
    return tfidf


def calc_sim(tfidf, c_tfidf):
    inter = set(tfidf.keys()) & set(c_tfidf.keys())
    ans = 0
    for item in inter:
        ans += tfidf[item] * c_tfidf[item]
    return ans


def keyword_exist(c_seg, seg):
    """判断两个名称中是否存在相同的关键词"""
    common = set(c_seg) & set(seg)
    for item in key_word:
        if item in common:
            return True
    return False


def get_cand(word, ans, seg, tfidf, reverse, alpha):
    """查询与当前名称匹配的候选结果"""
    for k in tfidf.keys():
        cands = reverse.get(k)
        if not cands:
            continue
        for cand in cands:
            if cand not in ans.keys():
                c_seg = list(seg_word(cand))
                if c_seg and len(c_seg) > 0:
                    c_tfidf = calc_tfidf(c_seg, reverse)
                    # 计算余弦相似度时会去除查询单词中的中英文标点符号
                    tmp = ''.join((filter(filter_func, strQ2B(word))))
                    l_dis = Levenshtein.ratio(tmp, cand)
                    # 如果两个名称完全相同则他们的相似度为1,
                    if l_dis == 1.0:
                        ans[cand] = 1.0
                    # 否则再考虑他们的余弦相似度
                    else:
                        tf_sim = calc_sim(tfidf, c_tfidf)
                        # ans[cand] = tf_sim * l_dis
                        ans[cand] = alpha * tf_sim + (1 - alpha) * l_dis
                        # 如果两个名称中有相同的关键词，则将他们的相似度值扩大1倍
                        if keyword_exist(seg, c_seg):
                            ans[cand] *= 2


def search(word, reverse, words, cnt):
    """查询word对应的标疾病名称及对应的icd码"""
    alpha = 0.8  # 确定tf_sim和l_dis的权重
    seg = list(seg_word(word))
    tfidf = calc_tfidf(seg, reverse)
    ans = {}
    word_cpy = word
    # 查询与当前名称匹配的候选名称
    for key in synonym:
        if key in word:
            word = word.replace(key, synonym[key])
            get_cand(word, ans, seg, tfidf, reverse, alpha)
    else:
        get_cand(word_cpy, ans, seg, tfidf, reverse, alpha)
    # 按照相似度选出候选结果中最匹配的前cnt个
    relevant = heapq.nlargest(cnt, ans.items(), key=lambda x: x[1])
    for i, r in enumerate(relevant):
        relevant[i] = r + (words.get(r[0]),)
    return relevant


def get_icd():
    # 获取标疾病名称表; 键: 疾病名称; 值: icd
    words_standard = load_words()
    # 获取实体(就是每个字)
    entity = load_entity(words_standard)
    # 包含指定实体词的标准疾病名称
    reverse = load_reverse(entity, words_standard)
    while True:
        word = input("input:")
        t_s = time.time()
        for item in search(word, reverse, words_standard, 3):
            print(item)
        t_e = time.time()
        print("查询用时:{}秒".format(t_e - t_s))


if __name__ == '__main__':
    get_icd()
