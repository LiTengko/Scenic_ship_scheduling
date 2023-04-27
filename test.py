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

# _*_ coding:utf-8 _*_
"""
@File     : model_generate.py
@Project  : MIP_solver
@Time     : 2023/4/13 13:22
@Author   : Li D.K
@Contact  : lidengke@zju.edu.cn
@Software : PyCharm
@License  : (C)Copyright 2022 SRTP
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2023/4/13 13:22   Li D.K.      1.0         None
-----------------------------------------------------
Feature description：
根据csv中的变量创建对应格式的变量
并创建模型，添加变量
"""

# import lib
import pandas as pd
import gurobipy as gb
import os
import model_index
from gurobipy import GRB
#
# def create_tau():
#     """
#     从 tau.csv中创建 multidict 变量
#     其中键为(i,j),以0表示g；值为tau_ij
#     tau_ij 以 tau[i,j]索引  arc为包含(i,j)的列表
#     :return: multidict变量,路径arcs 和 时间tau_ij
#     """
#     file_path = os.path.join(data_generate.output_folder, "tau.csv")
#     if not os.path.exists(file_path):
#         print("需要先生成tau.csv")
#     else:
#         # 读取数据表文件
#         df = pd.read_csv(file_path)
#         # 创建空字典
#         dict_ij = {}
#         # 遍历数据表，将每个(i,j)位置的值添加到字典中
#         for i in range(len(df.index)):
#             for j in range(len(df.columns)):
#                 key = (i, j)
#                 value = df.iloc[i, j]
#                 dict_ij[key] = value
#         # 打印字典
#         arcs, tau_ij = gb.multidict(dict_ij)
#         return arcs, tau_ij
#
# arcs, tau = create_tau()
# print(tau[1, 7])
# def create_Pv_ts():
#     """
#     从ts.csv生成字典变量PV和ts
#     :return: 字典变量PV，ts；其中PV[v_ID]，ts[v_ID,p] (注意！ts中p不包含大门 0)
#     """
#     file_path = os.path.join(model_index.output_folder, "ts.csv")
#     if not os.path.exists(file_path):
#         print("需要先生成ts.csv")
#     else:
#         # 读取 CSV 文件
#         data = pd.read_csv(file_path)
#         # 根据给定的规则生成字典变量 PV
#         Pv = {}
#         ts = {}
#         for index, row in data.iterrows():
#             Pv[row['ID']] = [idx for idx, value in enumerate(row) if value > 5 and idx != 0]  # 跳过 ID 列
#             for i in range(1, 8):  # 从 1 到 7（包含）
#                 ts[row['ID'], i] = row[i]
#         return gb.tupledict(Pv), gb.tupledict(ts)
#
# Pv, ts = create_Pv_ts()  # PV[v_ID] ts[v_ID,p] (p不包含大门 0)
#
# print(Pv[1])

# import math
# print(math.ceil(1.1))
# _*_ coding:utf-8 _*_


# import lib
import gurobipy as gp

# 读取 MPS 文件并创建 Gurobi 模型对象
model2 = gp.read("./data/price_2_small_c4_1.MPS")


# 对模型进行求解
model2.optimize()
# 设置最大求解时间为120min
model2.Params.TimeLimit = 7200

# 输出变量的解值
for v in model2.getVars():
    if (v.x - 0) != 0:
        print(f"{v.varName}: {v.x}")
