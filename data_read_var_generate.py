# _*_ coding:utf-8 _*_
"""
@File     : data_read_var_generate.py
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

# 指定系数
P_all_a = 80  # 一票制票价
P_all_b = 50  # 两部制票价
c1 = 1  # 票价系数c1
c2 = 2  # 固定成本系数c2
c3 = 2  # 行驶成本系数c3
c4 = 1  # 等待成本系数c4


def create_tau():
    """
    从 tau.csv中创建 multidict 变量
    其中键为(i,j),以0表示g；值为tau_ij
    :return: multidict变量,路径arcs 和 时间tau_ij
    """
    file_path = os.path.join(data_generate.output_folder, "tau.csv")
    if not os.path.exists(file_path):
        print("需要先生成tau.csv")
    else:
        # 读取数据表文件
        df = pd.read_csv(file_path)
        # 创建空字典
        dict_ij = {}
        # 遍历数据表，将每个(i,j)位置的值添加到字典中
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                key = (i, j)
                value = df.iloc[i, j]
                dict_ij[key] = value
        # 打印字典
        arcs, tau_ij = gb.multidict(dict_ij)
        return arcs, tau_ij


def create_Nv_TE():
    """
    从 visitor.csv中创建 multidict 变量
    其中键为v_ID,两字典的值分别为Nv和TE
    :return: Nv,TE
    """
    file_path = os.path.join(data_generate.output_folder, "visitor.csv")
    if not os.path.exists(file_path):
        print("需要先生成visitor.csv")
    else:
        # 读取 CSV 文件
        df = pd.read_csv(file_path)

        # 将 ID 列设置为数据帧的索引
        df.set_index('ID', inplace=True)

        # 创建 Nv 和 TE 字典
        Nv = gb.tupledict(df['NV'].to_dict())
        TE = gb.tupledict(df['TE'].to_dict())
    return Nv, TE


def create_Pv_ts():
    """
    从ts.csv生成字典变量PV和ts
    :return: 字典变量PV，ts；其中PV[v_ID]，ts[v_ID,p]
    """
    file_path = os.path.join(data_generate.output_folder, "ts.csv")
    if not os.path.exists(file_path):
        print("需要先生成ts.csv")
    else:
        # 读取 CSV 文件
        data = pd.read_csv(file_path)
        # 根据给定的规则生成字典变量 PV
        Pv = {}
        ts = {}
        for index, row in data.iterrows():
            Pv[row['ID']] = [idx for idx, value in enumerate(row) if value != -1 and idx != 0]  # 跳过 ID 列
            for i in range(1, 8):  # 从 1 到 7（包含）
                ts[row['ID'], i] = row[i]
        return gb.tupledict(Pv), gb.tupledict(ts)


if not os.path.exists(data_generate.output_folder):
    print("需要先运行data_generate.py")
else:
    #  代码主体

    # 由数据表生成multidict变量
    arcs, tau = create_tau()
    # print(arcs)
    # print(tau_ij)
    Nv, TE = create_Nv_TE()
    # print(Nv)
    # print(TE)
    Pv, ts = create_Pv_ts()

    # 生成tuplelist变量
    v_ID = gb.tuplelist([x for x in range(1, data_generate.V_NUM + 1)])
    P = gb.tuplelist([x for x in range(0, data_generate.P_NUM+1)])
    b = gb.tuplelist([x for x in range(1, data_generate.B_NUM + 1)])

    R = gb.tupledict()
    for key in range(1, data_generate.B_NUM + 1):
        R[key] = list(range(1, data_generate.R_MAX + 1))


    m = gb.Model("test1")
    # 决策变量
    x = m.addVars(v_ID, arcs, b, R, vtype=GRB.BINARY, name="x")  # x_vijbr
    y = m.addVars(arcs, b, R, vtype=GRB.BINARY, name="y")  # y_ijbr
    L = m.addVars(v_ID, P, vtype=GRB.BINARY, name="L")  # L_vi

    # 时间变量
    z_GA = m.addVars(P, v_ID, vtype=GRB.CONTINUOUS, name="z_GA")  # z^GA_iv
    z_GD = m.addVars(P, v_ID, vtype=GRB.CONTINUOUS, name="z_GD")  # z^GD_iv
    z_BF = m.addVars(R, b, vtype=GRB.CONTINUOUS, name="z_BF")  # z^BF_rb
    z_BS = m.addVars(R, b, vtype=GRB.CONTINUOUS, name="z_BS")  # z^BS_rb

    # 目标函数各项 （一票制）
    price_all = P_all_a * gb.quicksum(c1 * Nv[v_i] for v_i in Nv)  # [1.1]
    fix_cost = gb.quicksum(c2 * y[0, j_i, b_i, 1] for j_i in P for b_i in b)  # [1.3]
    operate_cost = gb.quicksum(c3 * tau[i_i, j_i] * y[i_i, j_i, b_i, r_i]
                               for i_i, j_i in arcs for b_i in b for r_i in R)  # [1.4]
    # wait_cost = gb.quicksum((c4 * (z_GD[i_i, v_i] - z_GA[i_i, v_i] - ts[i_i, v_i]) + c4*(z_GD[0, v_i] - TE[v_i])
    #                         for i_i in Pv[v_i]) for v_i in v_ID)
    wait_cost1 = gb.quicksum(gb.quicksum(c4 * z_GD[i_i, v_i] for i_i in Pv[v_i]) for v_i in v_ID)
    wait_cost2 = gb.quicksum(gb.quicksum(c4 * z_GA[i_i, v_i] for i_i in Pv[v_i])for v_i in v_ID)
    wait_cost3 = gb.quicksum(gb.quicksum(c4 * ts[v_i, i_i] for i_i in Pv[v_i]) for v_i in v_ID)
    wait_cost4 = gb.quicksum(c4 * z_GD[0, v_i] for v_i in v_ID)
    wait_cost5 = gb.quicksum(c4 * TE[v_i] for v_i in v_ID)
    wait_cost = wait_cost1 - wait_cost2 - wait_cost3 + wait_cost4 - wait_cost5
    # 设定目标函数
    m.setObjective(price_all - fix_cost - operate_cost - wait_cost, GRB.MAXIMIZE)

    # 设定约束
    m.addConstrs((
        gb.quicksum(
            gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i]) for r_i in R[b_i]) for b_i in b) + L[
            v_i, i_i] == 1
        for v_i in v_ID for i_i in P
    ), name="[1.7]")
    m.write("./data/test1.lp")
