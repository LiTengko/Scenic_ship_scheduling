# _*_ coding:utf-8 _*_
"""
@File     : data_generate.py
@Project  : MIP_solver
@Time     : 2023/4/12 13:13
@Author   : Li D.K
@Contact  : lidengke@zju.edu.cn
@Software : PyCharm
@License  : (C)Copyright 2022 SRTP
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2023/4/12 13:13   Li D.K.      1.0         None
-----------------------------------------------------
Feature description：
Generate corresponding data
store the data in excel format in the directory ./data
and refer to the documentation for the method of generating data.
"""

# import lib
import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np
import os

'''
静态变量指定
P_NUM 内部景点数
V_NUM 游团数量
B_NUM 游船数量
Cb    游船载客量
R_MAX 每船最大行程数
'''
P_NUM = 7
V_NUM = 500
B_NUM = 30
Cb = 35
R_MAX = 20


def generate_time_slots(N):
    """
    入园时间生成
    7-10，10-15，15-17的比例分别指定为0.6，0.3，0.1
    :param N: the num of the list
    :return: list variable
    """
    time_slots = []
    # 按比例分配时间段内的数量
    first_slot_count = int(N * 0.6)
    second_slot_count = int(N * 0.3)
    third_slot_count = N - first_slot_count - second_slot_count

    # 定义时间段
    first_slot_start = datetime.strptime("07:00", "%H:%M")
    first_slot_end = datetime.strptime("10:00", "%H:%M")

    second_slot_start = datetime.strptime("10:01", "%H:%M")
    second_slot_end = datetime.strptime("15:00", "%H:%M")

    third_slot_start = datetime.strptime("15:00", "%H:%M")
    third_slot_end = datetime.strptime("17:00", "%H:%M")

    for _ in range(first_slot_count):
        time_diff = (first_slot_end - first_slot_start).total_seconds() // 60
        random_minutes = random.randint(0, time_diff)
        random_time = first_slot_start + timedelta(minutes=random_minutes)
        time_slots.append(random_time.strftime("%H:%M"))

    for _ in range(second_slot_count):
        time_diff = (second_slot_end - second_slot_start).total_seconds() // 60
        random_minutes = random.randint(0, time_diff)
        random_time = second_slot_start + timedelta(minutes=random_minutes)
        time_slots.append(random_time.strftime("%H:%M"))

    for _ in range(third_slot_count):
        time_diff = (third_slot_end - third_slot_start).total_seconds() // 60
        random_minutes = random.randint(0, time_diff)
        random_time = third_slot_start + timedelta(minutes=random_minutes)
        time_slots.append(random_time.strftime("%H:%M"))

    # 打乱时间顺序
    random.shuffle(time_slots)
    return time_slots


def generate_Nv(N):
    """
    游览时间生成
    高斯分布均值指定为5
    :param N: the num of the list
    :return: list variable
    """
    mean = 5
    sigma = 1
    min_val = 1
    gaussian_integers = np.random.normal(mean, sigma, N)
    clipped_gaussian_integers = np.clip(gaussian_integers, min_val, None)
    result = np.round(clipped_gaussian_integers).astype(int).tolist()
    return result


def generate_ts_matrix(size):
    """
    生成游览时间矩阵，对应位置(i,j)对应到tau_ij
    这里生成的为10~30的随机数
    :param size: 矩阵的规模
    :return: matrix
    """
    matrix = np.random.randint(10, 31, (size, size))
    # 上三角转置合并后形成对角矩阵
    ts_matrix = np.triu(matrix) + np.triu(matrix, 1).T
    # 主对角线元素为0
    np.fill_diagonal(ts_matrix, 0)
    return ts_matrix


output_folder = "./data"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

"""
# visitor 数据表生成
visitor_num = generate_Nv(V_NUM)
time_slots = generate_time_slots(V_NUM)
visitor_dict = {
    'ID': list(range(1, V_NUM+1)),
    'TE': time_slots,
    'NV': visitor_num,
}
visitor_data = pd.DataFrame(visitor_dict)
# print(visitor_data.head())
output_file = os.path.join(output_folder, "visitor.csv")
visitor_data.to_csv(output_file, index=False)
"""

# ts 数据表生成
# 包含有大门，因此最终矩阵规模为 P_NUM + 1
ts_matrix = generate_ts_matrix(P_NUM + 1)
# print(ts_matrix)
ts_data = pd.DataFrame(ts_matrix)
ts_data.columns = ['g', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
output_file = os.path.join(output_folder, "ts.csv")
ts_data.to_csv(output_file, index=False)

