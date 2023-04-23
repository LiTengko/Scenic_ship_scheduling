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
import data_generate
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
R = gb.tupledict()
for key in range(1, data_generate.B_NUM + 1):
    R[key] = list(range(1, data_generate.R_MAX + 1))

print(R[2])