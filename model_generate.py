# _*_ coding:utf-8 _*_
"""
@File     : model_generate.py
@Project  : MIP_solver
@Time     : 2023/4/13 13:22
@Author   : Li D.K
@Contact  : lidengke@zju.edu.cn
@Software : PyCharm
@License  : (C)Copyright 2022 SRTP
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

# 指定系数
P_all_a = 80  # 一票制票价
P_all_b = 50  # 两部制票价
pm = gb.tupledict({1: 10, 2: 15, 3: 10, 4: 15, 5: 10, 6: 15, 7: 10})  # 两部制下各景点票价
c1 = 3   # 票价系数c1
c2 = 1   # 固定成本系数c2
c3 = 2   # 行驶成本系数c3
c4 = 1   # 等待成本系数c4

M = 100000  # 大整数
e = 1  # 小整数

TE = 570  # 设置最晚入园时间为16:30,计算与7：00的差值为570 min  注意！设置TE时应小于游客入园时间TE


def create_tau():
    """
    从 tau.csv中创建 multidict 变量
    其中键为(i,j),以0表示g；值为tau_ij
    tau_ij 以 tau[i,j]索引  arc为包含(i,j)的列表
    :return: multidict变量,路径arcs 和 时间tau_ij
    """
    file_path = os.path.join(model_index.output_folder, "tau.csv")
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


def create_Nv_Te():
    """
    从 visitor.csv中创建 multidict 变量
    其中键为v_ID,两字典的值分别为Nv和TE,两者索引分别为 Nv[v_ID] TE[v_ID]
    :return: Nv,TE
    """
    file_path = os.path.join(model_index.output_folder, "visitor.csv")
    if not os.path.exists(file_path):
        print("需要先生成visitor.csv")
    else:
        # 读取 CSV 文件
        df = pd.read_csv(file_path)

        # 将 ID 列设置为数据帧的索引
        df.set_index('ID', inplace=True)

        # 创建 Nv 和 TE 字典
        Nv = gb.tupledict(df['NV'].to_dict())
        Te = gb.tupledict(df['TE'].to_dict())
    return Nv, Te


def create_Pv_ts():
    """
    从ts.csv生成字典变量PV和ts
    :return: 字典变量PV，ts；其中PV[v_ID]，ts[v_ID,p] (注意！ts中p不包含大门 0)
    """
    file_path = os.path.join(model_index.output_folder, "ts.csv")
    if not os.path.exists(file_path):
        print("需要先生成ts.csv")
    else:
        # 读取 CSV 文件
        data = pd.read_csv(file_path)
        # 根据给定的规则生成字典变量 PV
        Pv = {}
        ts = {}
        for index, row in data.iterrows():
            Pv[row['0']] = [idx for idx, value in enumerate(row) if value > 5 and idx != 0]  # 跳过 ID 列
            for i in range(1, model_index.P_NUM + 1):  # 从 1 到 P_NUM
                ts[row['0'], i] = row[i]
        return gb.tupledict(Pv), gb.tupledict(ts)


if not os.path.exists(model_index.output_folder):
    print("需要先运行data_generate.py")
else:
    """=============  代码主体  ==============="""
    '''集合的创建'''
    # 由枚举生成
    V_ID = gb.tuplelist([x for x in range(1, model_index.V_NUM + 1)])  # 编号：1-V_NUM
    P = gb.tuplelist([x for x in range(0, model_index.P_NUM + 1)])  # 编号：0-P_NUM *0代指g
    B = gb.tuplelist([x for x in range(1, model_index.B_NUM + 1)])  # 编号：1-B_NUM
    # 由数据表生成
    arcs, tau = create_tau()  # arc[(i,j)] tau[i,j]
    Nv, Te = create_Nv_Te()  # Nv[v_ID] TE[v_ID]
    Pv, ts = create_Pv_ts()  # PV[v_ID] ts[v_ID,p] (p不包含大门 0)
    R = gb.tupledict()
    for key in range(1, model_index.B_NUM + 1):
        R[key] = list(range(1, model_index.R_MAX + 1))

    '''模型创建'''
    m = gb.Model("test1")

    '''决策变量'''
    # 0-1 变量
    x = m.addVars(V_ID, arcs, B, R[1], vtype=GRB.BINARY, name="x")  # x_vijbr (36)
    y = m.addVars(arcs, B, R[1], vtype=GRB.BINARY, name="y")  # y_ijbr (37)
    L = m.addVars(V_ID, P, vtype=GRB.BINARY, name="L")  # L_vi (38)
    # 时间整型变量
    z_GA = m.addVars(V_ID, P, vtype=GRB.INTEGER, name="z_GA")  # z^GA_vi
    z_GD = m.addVars(V_ID, P, vtype=GRB.INTEGER, name="z_GD")  # z^GD_vi
    z_BF = m.addVars(R[1], B, vtype=GRB.INTEGER, name="z_BF")  # z^BF_rb
    z_BS = m.addVars(R[1], B, vtype=GRB.INTEGER, name="z_BS")  # z^BS_rb

    """目标函数"""
    # 一票制票价
    price_1 = gb.quicksum(P_all_a * c1 * Nv[v_i] for v_i in V_ID)  # (1)
    # 两部制票价
    p_separate = gb.quicksum(
        gb.quicksum(
            gb.quicksum(
                gb.quicksum(
                    gb.quicksum(c1 * pm[j_i] * Nv[v_i] * x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i])
                    for i_i in Pv[v_i] + [0])
                for r_i in R[b_i])
            for b_i in B)
        for v_i in V_ID)
    price_2 = p_separate + gb.quicksum(P_all_b * c1 * Nv[v_i] for v_i in V_ID)  # (2)
    # 固定成本
    fix_cost = gb.quicksum(gb.quicksum(c2 * y[0, j_i, b_i, 1] for j_i in P if j_i != 0) for b_i in B)  # (3)
    # 运营成本
    operate_cost = gb.quicksum(
        gb.quicksum(
            gb.quicksum(
                gb.quicksum(c3 * tau[i_i, j_i] * y[i_i, j_i, b_i, r_i]
                            for j_i in P) for i_i in P)
            for r_i in R[b_i])
        for b_i in B)  # (4)
    # 计算等待成本
    wait_cost_1 = gb.quicksum(
        gb.quicksum(c4 * (z_GD[v_i, i_i] - z_GA[v_i, i_i] - ts[v_i, i_i]) * (1 - L[v_i, i_i])
                    for i_i in Pv[v_i])
        for v_i in V_ID)  # (6)
    wait_cost = wait_cost_1 + gb.quicksum(c4 * (z_GD[v_i, 0] - Te[v_i]) for v_i in V_ID)  # (5) & (6) & (7)

    # 设定目标函数
    # m.setObjective(price_1 - fix_cost - operate_cost - wait_cost, GRB.MAXIMIZE)  # (9)
    m.setObjective(price_2 - fix_cost - operate_cost - wait_cost, GRB.MAXIMIZE)  # (10)

    """设定约束"""
    m.addConstrs((
        (gb.quicksum(
            gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i]) for r_i in R[b_i]) for b_i in
            B)
         + L[v_i, i_i] == 1)
        for v_i in V_ID for i_i in Pv[v_i] + [0]
    ), name="(10)")

    m.addConstrs((
        (gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for r_i in R[b_i]) for b_i in B)
                     for i_i in Pv[v_i] + [0]) <= 1)
        for v_i in V_ID for j_i in Pv[v_i]
    ), name="(11)")

    m.addConstrs((
        gb.quicksum(
            gb.quicksum(gb.quicksum(x[v_i, 0, j_i, b_i, r_i] for j_i in Pv[v_i]) for r_i in R[b_i]) for b_i in B) == 1
        for v_i in V_ID
    ), name="(12)")

    m.addConstrs((
        (gb.quicksum(
            gb.quicksum(gb.quicksum(x[v_i, i_i, 0, b_i, r_i] for i_i in Pv[v_i]) for r_i in R[b_i]) for b_i in B) == 1)
        for v_i in V_ID
    ), name="(13)")

    m.addConstrs((
        (gb.quicksum(gb.quicksum(y[i_i, j_i, b_i, r_i] for j_i in P) for i_i in P) <= 1)
        for b_i in B for r_i in R[b_i]
    ), name="(14)")

    m.addConstrs((
        (gb.quicksum(y[i_i, i_i, b_i, r_i] for i_i in P) == 0)
        for b_i in B for r_i in R[b_i]
    ), name="(15)")

    m.addConstrs((
        (gb.quicksum(gb.quicksum(y[i_i, j_i, b_i, r_i] for j_i in P) for i_i in P) <= gb.quicksum(
            gb.quicksum(y[i_i, j_i, b_i, (r_i - 1)] for j_i in P) for i_i in P))
        for b_i in B for r_i in R[b_i] if r_i >= 2
    ), name="(16)")

    m.addConstrs((
        (gb.quicksum(y[j_i, l_i, b_i, r_i] for l_i in P) <= gb.quicksum(y[i_i, j_i, b_i, (r_i - 1)] for i_i in P))
        for b_i in B for r_i in R[b_i] if r_i >= 2 for j_i in P
    ), name="(17)")

    m.addConstrs((
        (gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, j_i, l_i, b_i, r_i] for r_i in R[b_i]) for b_i in B) for l_i in
                     Pv[v_i] + [0]) <=
         gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for r_i in R[b_i]) for b_i in B) for i_i in
                     Pv[v_i] + [0]))
        for v_i in V_ID for j_i in Pv[v_i]
    ), name="(18)")

    m.addConstrs((
        (gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, l_i, j_i, b_i, r_i] for r_i in R[b_i]) for b_i in B) for l_i in
                     Pv[v_i] + [0]) <=
         gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, j_i, i_i, b_i, r_i] for r_i in R[b_i]) for b_i in B) for i_i in
                     Pv[v_i] + [0]))
        for v_i in V_ID for j_i in Pv[v_i]
    ), name="(19)")

    m.addConstrs((
        (gb.quicksum(y[i_i, 0, b_i, r_i] for i_i in P if i_i != 0) >=
         (gb.quicksum(gb.quicksum(y[i_i, j_i, b_i, (r_i - 1)] for j_i in P if j_i != 0) for i_i in P) - gb.quicksum(
             gb.quicksum(y[i_i, j_i, b_i, r_i] for j_i in P if j_i != 0 & i_i != j_i) for i_i in P if i_i != 0)))
        for b_i in B for r_i in R[b_i] if r_i >= 2
    ), name="(20)")

    m.addConstrs((
        (gb.quicksum(y[0, j_i, b_i, 1] for j_i in P if j_i != 0) == gb.quicksum(
            gb.quicksum(y[i_i, j_i, b_i, 2] for j_i in P) for i_i in P))
        for b_i in B
    ), name="(21)")

    m.addConstrs((
        (gb.quicksum(Nv[v_i] * x[v_i, i_i, j_i, b_i, r_i] for v_i in V_ID) <= model_index.Cb * y[i_i, j_i, b_i, r_i])
        for i_i in P for j_i in P for b_i in B for r_i in R[b_i]
    ), name="(22)")

    m.addConstrs((
        (z_BF[r_i, b_i] == z_BS[r_i, b_i] + gb.quicksum(
            gb.quicksum(tau[i_i, j_i] * y[i_i, j_i, b_i, r_i] for j_i in P) for i_i in P))
        for b_i in B for r_i in R[b_i]
    ), name="(23)")

    m.addConstrs((
        (z_BS[r_i, b_i] >= z_BF[(r_i - 1), b_i])
        for b_i in B for r_i in R[b_i] if r_i >= 2
    ), name="(24)")

    m.addConstrs((
        (z_BS[r_i, b_i] >= z_GA[v_i, i_i] + ts[v_i, i_i] - M * (
                1 - gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i] + [0])))
        for b_i in B for r_i in R[b_i] for v_i in V_ID for i_i in Pv[v_i]
    ), name="(25)")

    m.addConstrs((
        (z_BS[r_i, b_i] >= Te[v_i] - M * (1 - gb.quicksum(x[v_i, 0, j_i, b_i, r_i] for j_i in Pv[v_i])))
        for b_i in B for r_i in R[b_i] for v_i in V_ID
    ), name="(26)")

    m.addConstrs((
        (z_GA[v_i, i_i] - TE <= M * L[v_i, i_i])
        for v_i in V_ID for i_i in Pv[v_i]
    ), name="(27)")

    m.addConstrs((
        (-z_GA[v_i, i_i] + TE - e <= M * (1 - L[v_i, i_i]))
        for v_i in V_ID for i_i in Pv[v_i]
    ), name="(28)")

    m.addConstrs((
        (z_GA[v_i, i_i] >= z_BF[r_i, b_i] - M * (1 - gb.quicksum(x[v_i, j_i, i_i, b_i, r_i] for j_i in Pv[v_i] + [0])))
        for b_i in B for r_i in R[b_i] for v_i in V_ID for i_i in Pv[v_i]
    ), name="(29)")

    m.addConstrs((
        (z_GA[v_i, i_i] <= z_BF[r_i, b_i] + M * (1 - gb.quicksum(x[v_i, j_i, i_i, b_i, r_i] for j_i in Pv[v_i] + [0])))
        for b_i in B for r_i in R[b_i] for v_i in V_ID for i_i in Pv[v_i]
    ), name="(30)")

    m.addConstrs((
        (z_GD[v_i, i_i] <= z_BS[r_i, b_i] + M * (1 - gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i] + [0])))
        for b_i in B for r_i in R[b_i] for v_i in V_ID for i_i in Pv[v_i] + [0]
    ), name="(31)")

    m.addConstrs((
        (z_GD[v_i, i_i] >= z_BS[r_i, b_i] - M * (1 - gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i] + [0])))
        for b_i in B for r_i in R[b_i] for v_i in V_ID for i_i in Pv[v_i] + [0]
    ), name="(32)")

    m.addConstrs((
        (z_GD[v_i, i_i] - z_GA[v_i, i_i] - ts[v_i, i_i]
         + M * (1 - gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i] + [0])
                                            for r_i in R[b_i]) for b_i in B))
         + M * (1 - gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, j_i, i_i, b_i, r_i] for j_i in Pv[v_i] + [0])
                                            for r_i in R[b_i]) for b_i in B)) >= 0)
        for v_i in V_ID for i_i in Pv[v_i]
    ), name="(33)")

    m.addConstrs((
        (z_GD[v_i, 0] - Te[v_i] >= 0) for v_i in V_ID
    ), name="(34)")

    m.addConstrs((
        (gb.quicksum(gb.quicksum(x[v_i, j_i, 0, b_i, r_i] for r_i in R[b_i]) for b_i in B) <= 1 + M * (
                1 - gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for r_i in R[b_i]) for b_i in B)) + M * L[
             v_i, i_i] + M * (1 - L[v_i, j_i]))
        for v_i in V_ID for i_i in Pv[v_i] for j_i in Pv[v_i]
    ), name="(35)")

    m.addConstrs((
        (gb.quicksum(gb.quicksum(x[v_i, j_i, 0, b_i, r_i] for r_i in R[b_i]) for b_i in B) >= 1 - M * (
                1 - gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for r_i in R[b_i]) for b_i in B)) - M * L[
             v_i, i_i] - M * (1 - L[v_i, j_i]))
        for v_i in V_ID for i_i in Pv[v_i] for j_i in Pv[v_i]
    ), name="(36)")

    """求解和输出"""
    # # 写入数据
    # m.write('./data/price_1_small.lp')
    m.write('./data/price_2_small_c4_1.MPS')

