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
visitor_data.to_csv("./data/visitor.csv", index=False)
