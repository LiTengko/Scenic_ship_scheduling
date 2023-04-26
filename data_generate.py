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
import model_index



def generate_time_slots(N):
    """
    入园时间生成
    7-10，10-15，15-16:30的比例分别指定为0.6，0.3，0.1
    :param N: the num of the list
    :return: list variable
    """
    time_slots = []
    # 按比例分配时间段内的数量
    first_slot_count = int(N * 0.7)
    second_slot_count = int(N * 0.2)
    third_slot_count = N - first_slot_count - second_slot_count

    # 定义时间段
    first_slot_start = datetime.strptime("07:00", "%H:%M")
    first_slot_end = datetime.strptime("10:00", "%H:%M")

    second_slot_start = datetime.strptime("10:01", "%H:%M")
    second_slot_end = datetime.strptime("15:00", "%H:%M")

    third_slot_start = datetime.strptime("15:00", "%H:%M")
    third_slot_end = datetime.strptime("16:30", "%H:%M")

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


def generate_tau_matrix(size):
    """
    生成路程时间矩阵，对应位置(i,j)对应到tau_ij
    这里生成的为35~90的随机数
    :param size: 矩阵的规模
    :return: matrix
    """
    matrix = np.random.randint(15, 35, (size, size))
    # 上三角转置合并后形成对角矩阵
    tau_matrix = np.triu(matrix) + np.triu(matrix, 1).T
    # 主对角线元素为0
    np.fill_diagonal(tau_matrix, 0)
    return tau_matrix





def time_period(time):
    """
    判断时间属于哪个时间段
    :param time: 时间格式变量
    :return: 时间段1，2，3
    """
    if time >= pd.Timestamp('1900-01-01 07:00:00') and time <= pd.Timestamp('1900-01-01 10:00:00'):
        return 1
    elif time > pd.Timestamp('1900-01-01 10:00:00') and time <= pd.Timestamp('1900-01-01 15:00:00'):
        return 2
    elif time > pd.Timestamp('1900-01-01 15:00:00') and time <= pd.Timestamp('1900-01-01 17:00:00'):
        return 3
    else:
        return -1


def ts_select(p_list):
    """
    根据输入的p_list生成均值不同的高斯分布
    :param p_list: 景点对应的序列
    :return: 返回的表示时间的list
    """
    ts_list = []
    # 定义字典, 对应不同景区游览时间的均值
    mean_values = {
        1: 40,
        2: 60,
        3: 40,
        4: 20,
        5: 40,
        6: 20,
        7: 50
    }

    for value in p_list:
        if value == -1:
            ts_list.append(-1)
        else:
            # 生成高斯分布整数并添加到新列表B
            gaussian_value = int(np.random.normal(mean_values[value], 10))
            ts_list.append(gaussian_value)

    return ts_list


def guss_int_generate(min_num, max_num):
    """
    以高斯分布形式生成[min,max]之间的随机数
    :param min:
    :param max:
    :return: int
    """
    mean = (min_num + max_num)/2  # 选择均值，使得整数范围在min到max之间
    std_dev = 0.85  # 标准差

    random_float = np.random.normal(loc=mean, scale=std_dev)
    random_integer = int(round(random_float))

    # 确保生成的整数在min到max之间
    random_integer = max(min(random_integer, max_num), min_num)

    return random_integer


def ts_generate(csv_file):
    """
    根据已有的csv_file生成游客在景区的停留时间
    并创建 ts.csv
    :param csv_file: visitor.csv 的文件路径
    :return: None
    """
    if os.path.exists(csv_file):
        # 读取CSV文件
        data = pd.read_csv(csv_file)
        # 将"TE"列转换为时间格式
        data['TE'] = pd.to_datetime(data['TE'], format="%H:%M")

        new_data = pd.DataFrame(columns=['ID', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7'])
        new_rows = []
        for index, row in data.iterrows():
            # 创建一个与景点数，所有元素初始化为-1
            row_list = [-1] * model_index.P_NUM

            # 读取"TE"列的数据
            time = row['TE']

            # 判断时间属于哪个时间段
            period = time_period(time)

            if period == 1:
                num_positions = guss_int_generate(4, 7)
            elif period == 2:
                num_positions = guss_int_generate(2, 4)
            elif period == 3:
                num_positions = guss_int_generate(1, 3)
            else:
                num_positions = 0

            # 随机选择列进行标记
            positions = random.sample(range(model_index.P_NUM), num_positions)
            for position in positions:
                row_list[position] = position + 1

            p_list = ts_select(row_list)
            # 添加新行到new_data DataFrame
            new_row = pd.DataFrame({
                'ID': [int(index) + 1],
                'P1': [p_list[0]],
                'P2': [p_list[1]],
                'P3': [p_list[2]],
                'P4': [p_list[3]],
                'P5': [p_list[4]],
                'P6': [p_list[5]],
                'P7': [p_list[6]]
            })

            new_rows.append(new_row)
        new_data = pd.concat(new_rows, ignore_index=True)
        output_file = os.path.join(model_index.output_folder, "ts.csv")
        new_data.to_csv(output_file, index=False)
    else:
        print("请检查是否已经生成visitor.csv")


def time_diff_in_minutes(time_str):
    """
    用于进行数据转换
    :param time_str:
    :return: 该时刻与7:00的差
    """
    base_time = datetime.strptime("07:00", "%H:%M")
    current_time = datetime.strptime(time_str, "%H:%M")
    time_diff = current_time - base_time
    return time_diff.seconds // 60

# visitor 数据表生成
visitor_num = generate_Nv(model_index.V_NUM)
time_slots = generate_time_slots(model_index.V_NUM)
visitor_dict = {
    'ID': list(range(1, model_index.V_NUM+1)),
    'TE': time_slots,
    'NV': visitor_num,
}
visitor_data = pd.DataFrame(visitor_dict)
# print(visitor_data.head())
output_file = os.path.join(model_index.output_folder, "visitor.csv")
visitor_data.to_csv(output_file, index=False)


'''数据生成，注释掉此部分以固定数据'''

"""
# tau 数据表生成
# 包含有大门，因此最终矩阵规模为 P_NUM + 1
tau_matrix = generate_tau_matrix(model_index.P_NUM + 1)
# print(tau_matrix)
tau_data = pd.DataFrame(tau_matrix)
tau_data.columns = ['g', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
output_file = os.path.join(model_index.output_folder, "tau.csv")
tau_data.to_csv(output_file, index=False)
"""
# ts 数据表生成
ts_generate('./data/visitor.csv')
# 替换TE为相距7:00的时间
df = pd.read_csv('./data/visitor.csv')
# Calculate the time difference and replace the 'TE' column
df['TE'] = df['TE'].apply(time_diff_in_minutes)
# Save the modified dataframe to the same CSV file
df.to_csv('./data/visitor.csv', index=False)

