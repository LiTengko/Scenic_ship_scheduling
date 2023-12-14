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
使用gb创建目标函数，约束，生成对应模型
"""

# import lib
import gurobipy as gb
import os
import model_index
from gurobipy import GRB
import data_read

# 指定需要生成的模型
'''
设置为1生成一票制模型
设置为2生成两部制模型
！！请不要设置为其他值
'''
Model = 1

# 指定系数
P_all_a = model_index.P_all_a  # 一票制票价
P_all_b = model_index.P_all_b  # 两部制票价
pm = gb.tupledict(model_index.pm)  # 两部制下各景点票价
c1 = model_index.c1   # 票价系数c1
c2 = model_index.c2   # 固定成本系数c2
c3 = model_index.c3   # 行驶成本系数c3
c4 = model_index.c4   # 等待成本系数c4
TE = model_index.TE   # 最晚入园时间

M = 5000  # 大整数
e = 1  # 小整数

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
    arcs, tau = gb.multidict(data_read.create_tau())  # arc[(i,j)] tau[i,j]

    Nv, Te = data_read.create_Nv_Te()  # Nv[v_ID] TE[v_ID]
    Nv = gb.tupledict(Nv)
    Te = gb.tupledict(Te)

    Pv, ts = data_read.create_Pv_ts()  # PV[v_ID] ts[v_ID,p] (p不包含大门 0)
    Pv = gb.tupledict(Pv)
    ts = gb.tupledict(ts)

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
    z_GA = m.addVars(V_ID, P, ub=600, lb=0, vtype=GRB.INTEGER, name="z_GA")  # z^GA_vi
    z_GD = m.addVars(V_ID, P, ub=600, lb=0, vtype=GRB.INTEGER, name="z_GD")  # z^GD_vi
    z_BF = m.addVars(R[1], B, ub=600, lb=0, vtype=GRB.INTEGER, name="z_BF")  # z^BF_rb
    z_BS = m.addVars(R[1], B, ub=600, lb=0, vtype=GRB.INTEGER, name="z_BS")  # z^BS_rb

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
    if Model == 1:
        # m.setObjective(price_1 - fix_cost - operate_cost - wait_cost, GRB.MAXIMIZE)  # (9)
        m.setObjective(price_1 - fix_cost - operate_cost, GRB.MAXIMIZE)  # (9)
        print("目标函数为price_1")
    else:
        m.setObjective(price_2 - fix_cost - operate_cost - wait_cost, GRB.MAXIMIZE)  # (10)
        print("目标函数为price_2")

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

    """输出模型"""
    if Model == 1:
        m.write('./data/price_1_small_c4_1.MPS')
        print("写入模型1")
    else:
        m.write('./data/price_2_small_c4_1.MPS')
        print("写入模型2")


def mycallback(model, where):
    if where == GRB.Callback.MIPSOL:
        # 在新的整数解中添加惰性约束
        # for v_i in V_ID:
        #     for i_i in Pv[v_i]:
        #         z_GD_val = model.cbGetSolution(z_GD[v_i, i_i])
        #         z_GA_val = model.cbGetSolution(z_GA[v_i, i_i])
        #
        #         x_val_1 = sum(
        #             model.cbGetSolution(x[v_i, i_i, j_i, b_i, r_i]) for j_i in Pv[v_i] + [0] for b_i in B for r_i in
        #             R[b_i])
        #         x_val_2 = sum(
        #             model.cbGetSolution(x[v_i, j_i, i_i, b_i, r_i]) for j_i in Pv[v_i] + [0] for b_i in B for r_i in
        #             R[b_i])
        #         if z_GD_val - z_GA_val - ts[v_i, i_i] + M * (1 - x_val_1) + M * (1 - x_val_2) >= 0:
        #             model.cbLazy(z_GD[v_i, i_i] - z_GA[v_i, i_i] - ts[v_i, i_i]
        #                          + M * (1 - gb.quicksum(
        #                 x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i] + [0] for b_i in B for r_i in R[b_i]))
        #                          + M * (1 - gb.quicksum(
        #                 x[v_i, j_i, i_i, b_i, r_i] for j_i in Pv[v_i] + [0] for b_i in B for r_i in R[b_i])) >= 0)

        for v_i in V_ID:
            for j_i in Pv[v_i]:
                # 创建约束表达式
                lhs_19 = gb.quicksum(
                    x[v_i, l_i, j_i, b_i, r_i] for l_i in Pv[v_i] + [0] for b_i in B for r_i in R[b_i]
                    if (v_i, l_i, j_i, b_i, r_i) in x)
                rhs_19 = gb.quicksum(
                    x[v_i, j_i, i_i, b_i, r_i] for i_i in Pv[v_i] + [0] for b_i in B for r_i in R[b_i]
                    if (v_i, j_i, i_i, b_i, r_i) in x)

                # 添加约束
                model.addConstr(lhs_19 <= rhs_19)

            #
            # # 添加约束(20)
            # for b_i in B:
            #     for r_i in R[b_i]:
            #         if r_i >= 2:
            #             lhs_20 = gb.quicksum(model.cbGetSolution(y[i_i, 0, b_i, r_i]) for i_i in P if i_i != 0)
            #             rhs_20_1 = gb.quicksum(
            #                 model.cbGetSolution(y[i_i, j_i, b_i, (r_i - 1)]) for i_i in P for j_i in P if j_i != 0)
            #             rhs_20_2 = gb.quicksum(model.cbGetSolution(y[i_i, j_i, b_i, r_i]) for i_i in P for j_i in P if
            #                            j_i != 0 and i_i != j_i)
            #             if lhs_20 is not None and rhs_20_1 is not None and rhs_20_2 is not None and lhs_20 >= (rhs_20_1 - rhs_20_2):
            #                 model.cbLazy(lhs_20 - (rhs_20_1 - rhs_20_2) >= 0)
