import re
import time
import pickle
import pandas as pd


def get_norm(df, file_name):
    """将标准表保存为字典的形式. 键: 名称; 值: icd"""
    ans = {}
    for _, v in df.iterrows():
        if pd.isnull(v[0]):
            v[0] = ""
        if pd.isnull(v[1]):
            v[1] = ""
        icd1 = re.sub(r"\s", "", v[0])
        icd2 = re.sub(r"\s", "", v[1])
        name = re.sub(r"\s", "", v[2])
        tmp = ",".join([icd1, icd2])
        if tmp.endswith(","):
            tmp = tmp[:-1]
        ans[name] = tmp
    with open('./data_result/' + file_name, mode='wb') as f:
        pickle.dump(ans, f)
    return ans


def get_input():
    """将输入数据按疾病名称去重, 并保存为列表的形式. 列表中的元素形式: (名称, icd)"""
    ans = []
    with open('./data_raw/淮河医院诊断名称及编码-20190423-尹茂林V1.csv', mode='r', encoding='utf8') as f:
        unique = list()
        for line in f:
            tmp = line.split('code')
            name = re.sub(r'\s', '', tmp[0])
            # 只保留名称不重复的疾病及其icd
            if name and name not in unique:
                unique.append(name)
                icd = re.sub(r'\s|=', '', tmp[1])
                if icd:
                    ans.append((name, icd))
                else:
                    ans.append((name, None))
    # 持久化
    with open('./data_result/input_name.pkl', mode='wb') as f:
        pickle.dump(ans, f)
    return ans


if __name__ == '__main__':
    t_s = time.time()
    """step1:将icd标准转为csv"""
    df_icd9 = pd.read_excel('data_raw/手术操作分类代码国家临床版2.0.xlsx')
    df_icd10 = pd.read_excel('data_raw/疾病分类与代码国家临床版2.0.xlsx')
    filename_icd9 = 'standard_icd9.pkl'
    filename_icd10 = 'standard_icd10.pkl'
    icd9 = get_norm(df_icd9, filename_icd9)
    print("标准手术名称共计{}条。".format(len(icd9)))
    # print(icd9)
    icd10 = get_norm(df_icd10, filename_icd10)
    print("标准疾病名称共计{}条。".format(len(icd10)))
    # print(icd10)
    t = time.time()
    """step2:将给定的疾病名称转为csv, 并做去重处理"""
    # name_input = get_input()
    # print(name_input)
    # print("需要查询的疾病名称去重后共计{}条。".format(len(name_input)))
    # t = time.time()
    print("用时：{}秒。".format(t - t_s))
    print('done')
