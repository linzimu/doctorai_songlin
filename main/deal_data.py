import time
import pickle
from model.get_icd import search
from model.get_icd import load_words
from model.get_icd import load_entity
from model.get_icd import load_reverse


def get_data(filepath='../data/data_result/input_name.pkl'):
    with open(filepath, 'rb') as f:
        records = pickle.load(f)
    data, data_y = [], []
    for item in records:
        if item[1] is None:
            data.append(item)
        else:
            data_y.append(item)
    print('有icd码的疾病数量：', len(data_y))
    print('无icd码的疾病数量：', len(data))
    return data, data_y


def get_res():
    data, data_y = get_data()
    words = load_words()
    entity = load_entity(words)
    reverse = load_reverse(entity, words, filepath="../model/tmp/reverse.pkl")
    ans = []
    for i, item in enumerate(data_y + data, 1):
        tmp = []
        res = search(item[0], reverse, words, 3)
        tmp.append(item)
        tmp.extend(res)
        print(i, tmp)
        ans.append(tmp)
        if i == 50:
            break
    return ans


if __name__ == '__main__':
    t_s = time.time()
    ans = get_res()
    with open("./匹配结果(输入有icd).csv", mode="w", encoding="utf8") as f:
        f.write("输入疾病名称及其对应icd￥匹配结果1及其对应icd￥匹配结果2及其对应icd￥匹配结果3及其对应icd\n")
        for item in ans:
            f.write("￥".join(map(str, item)) + '\n')
    t_e = time.time()
    print("用时:{}秒".format(t_e - t_s))
