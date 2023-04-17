# _*_ coding:utf-8 _*_
"""
@File     : test.py
@Project  : MIP_solver
@Time     : 2023/4/13 13:40
@Author   : Li D.K
@Contact  : lidengke@zju.edu.cn
@Software : PyCharm
@License  : (C)Copyright 2022 SRTP
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2023/4/13 13:40   Li D.K.      1.0         None
-----------------------------------------------------
Feature description：
"""

# import lib
import pandas as pd
import gurobipy as gb
from gurobipy import GRB

# # 读取 CSV 文件
# data = pd.read_csv('./data/ts.csv')
#
# # 根据给定的规则生成字典变量 PV
# PV = {}
# ts = {}
# for index, row in data.iterrows():
#     PV[row['ID']] = [idx for idx, value in enumerate(row) if value != -1 and idx != 0]  # 跳过 ID 列
#     for i in range(1, 8):  # 从 1 到 7（包含）
#         ts[row['ID'], i] = row[i]
# # 打印生成的字典变量 PV
# print(ts[2,5])
m = {1:10, 2:15, 3:10, 4: 5, 5:10, 6:5, 7:10}
print(m[7])