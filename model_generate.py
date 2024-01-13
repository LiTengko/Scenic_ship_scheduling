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

M = 10000  # 大整数
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

    A = data_read.creat_Aij()
    A = gb.tupledict(A)

    R = gb.tupledict()
    for key in range(1, model_index.B_NUM + 1):
        R[key] = list(range(1, model_index.R_MAX + 1))

    '''模型创建'''
    m = gb.Model("test1")

    '''决策变量'''
    # 0-1 变量
    x = m.addVars(V_ID, arcs, B, R[1], vtype=GRB.BINARY, name="x")  # x_vijbr
    y = m.addVars(arcs, B, R[1], vtype=GRB.BINARY, name="y")  # y_ijbr
    # 时间整型变量
    z_GA = m.addVars(V_ID, P, lb=0, ub=700, vtype=GRB.INTEGER, name="z_GA")  # z^GA_vi
    z_GD = m.addVars(V_ID, P, lb=0, ub=700, vtype=GRB.INTEGER, name="z_GD")  # z^GD_vi
    z_BF = m.addVars(R[1], B, lb=0, ub=700, vtype=GRB.INTEGER, name="z_BF")  # z^BF_rb
    z_BS = m.addVars(R[1], B, lb=0, ub=700, vtype=GRB.INTEGER, name="z_BS")  # z^BS_rb
    '''辅助变量'''
    L = m.addVars(V_ID, P, vtype=GRB.BINARY, name="L")  # L_vi
    TC_V = m.addVars(V_ID, vtype=GRB.BINARY, name="TC_V")  # TC^V_v
    TC = m.addVars(V_ID, P, vtype=GRB.BINARY, name="TC")  # TC_vi
    L_TC = m.addVars(V_ID, P, vtype=GRB.BINARY, name="L_TC")  # L^TC_vi
    I_br = m.addVars(B, R[1], vtype=GRB.BINARY, name="I_br")  # I_br
    I1_br = m.addVars(B, R[1], vtype=GRB.BINARY, name="I1_br")  # I1_br
    I2_br = m.addVars(B, R[1], vtype=GRB.BINARY, name="I2_br")  # I2_br
    Price = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Price")  # Price
    Fix_cost = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Fix_cost")  # Fix_cost
    Operate_cost = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Operate_cost")  # Operate_cost
    Wait_cost = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Wait_cost") # Wait_cost


    """目标函数"""
    '''
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
    # wait_cost_1 = gb.quicksum(
    #     gb.quicksum(c4 * (z_GD[v_i, i_i] - z_GA[v_i, i_i] - ts[v_i, i_i]) * (1 - L[v_i, i_i])
    #                 for i_i in Pv[v_i])
    #     for v_i in V_ID)  # (6)
    wait_cost_1 = gb.quicksum(
        gb.quicksum(c4 * (z_GD[v_i, i_i] - z_GA[v_i, i_i] - ts[v_i, i_i]) * gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, j_i, i_i, b_i, r_i] for j_i in Pv[v_i] + [0]) for r_i in R[b_i]) for b_i in B)
                    for i_i in Pv[v_i])
        for v_i in V_ID)  # (6)
    wait_cost = wait_cost_1 + gb.quicksum(c4 * (z_GD[v_i, 0] - Te[v_i]) for v_i in V_ID)  # (5) & (6) & (7)
    '''

    # 设定目标函数
    m.setObjective(Price - Fix_cost - Operate_cost - Wait_cost, GRB.MAXIMIZE)  # (8) & (9)

    """设定目标函数子项约束"""
    m.addConstr((Fix_cost == gb.quicksum(gb.quicksum(c2 * y[0, j_i, b_i, 1] for j_i in P if j_i != 0) for b_i in B)), name="(3)")

    m.addConstr((Operate_cost == gb.quicksum(
        gb.quicksum(
            gb.quicksum(
                gb.quicksum(c3 * tau[i_i, j_i] * y[i_i, j_i, b_i, r_i]
                            for j_i in P) for i_i in P)
            for r_i in R[b_i])
        for b_i in B)), name="(4)")

    # m.addConstr((Wait_cost == gb.quicksum(
    #     gb.quicksum(c4 * (z_GD[v_i, i_i] - z_GA[v_i, i_i] - ts[v_i, i_i]) * gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, j_i, i_i, b_i, r_i] for j_i in Pv[v_i] + [0]) for r_i in R[b_i]) for b_i in B)
    #                 for i_i in Pv[v_i])
    #     for v_i in V_ID) + gb.quicksum(c4 * ((z_GD[v_i, 0] - Te[v_i]) + gb.quicksum((z_GD[v_i, i_i] - z_GA[v_i, 0]) * gb.quicksum(gb.quicksum(x[v_i, i_i, 0, b_i, r_i] for r_i in R[b_i])for b_i in B) for i_i in Pv[v_i])) for v_i in V_ID)), name="(5.6.7)")
    m.addConstr((Wait_cost == gb.quicksum(
        gb.quicksum(c4 * (z_GD[v_i, i_i] - z_GA[v_i, i_i] - ts[v_i, i_i]) * gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i] + [0]) for r_i in R[b_i]) for b_i in B)for i_i in Pv[v_i]) for v_i in V_ID)
                 + gb.quicksum(c4 * (z_GD[v_i, 0] - Te[v_i]) for v_i in V_ID)), name="(5.6.7)")

    if Model == 1:
        m.addConstr((Price == gb.quicksum(P_all_a * c1 * Nv[v_i] for v_i in V_ID)), name="(1)")
        print("目标函数为price_1")
    else:
        m.addConstr((Price == gb.quicksum(
        gb.quicksum(
            gb.quicksum(
                gb.quicksum(
                    gb.quicksum(c1 * pm[j_i] * Nv[v_i] * x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i])
                    for i_i in Pv[v_i] + [0])
                for r_i in R[b_i])
            for b_i in B)
        for v_i in V_ID) + gb.quicksum(P_all_b * c1 * Nv[v_i] for v_i in V_ID)), name="(2)")
        print("目标函数为price_2")

    """约束条件"""
    m.addConstrs((
        (L_TC[v_i, i_i] == 0) >> (gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i]) for r_i in R[b_i]) for b_i in B) == 1)
        for v_i in V_ID for i_i in Pv[v_i] + [0]
    ), name="(10.1)")

    m.addConstrs((
        (L_TC[v_i, j_i] == 0) >>(gb.quicksum(
            gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for i_i in Pv[v_i] + [0]) for r_i in R[b_i]) for b_i in
            B) == 1)
        for v_i in V_ID for j_i in Pv[v_i] + [0]
    ), name="(10.2)")

    """
    m.addConstrs((
        (gb.quicksum(
            gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i] + [0]) for r_i in R[b_i]) for b_i in B)
         + M * L[v_i, i_i] >= 1)
        for v_i in V_ID for i_i in Pv[v_i] + [0]
    ), name="(10.1)")

    m.addConstrs((
        (gb.quicksum(
            gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i] + [0]) for r_i in R[b_i]) for b_i in
            B)
         - M * L[v_i, i_i] <= 1)
        for v_i in V_ID for i_i in Pv[v_i] + [0]
    ), name="(10.2)")

    m.addConstrs((
        (gb.quicksum(
            gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] - M * L[v_i, i_i] for j_i in Pv[v_i] + [0]) for r_i in R[b_i]) for b_i in
            B) <= 1)
        for v_i in V_ID for i_i in Pv[v_i] + [0]
    ), name="(10.3)")

    m.addConstrs((
        (gb.quicksum(
            gb.quicksum(
                gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] + M * L[v_i, i_i] for j_i in Pv[v_i] + [0]) for r_i in R[b_i])
            for b_i in
            B) >= 1)
        for v_i in V_ID for i_i in Pv[v_i] + [0]
    ), name="(10.4)")
    """

    # m.addConstrs((
    #     (gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for r_i in R[b_i]) for b_i in B)
    #                  for i_i in Pv[v_i] + [0]) <= 1)
    #     for v_i in V_ID for j_i in Pv[v_i]
    # ), name="(11.1)")

    m.addConstrs((
        gb.quicksum(
            gb.quicksum(gb.quicksum(x[v_i, 0, j_i, b_i, r_i] for j_i in Pv[v_i]) for r_i in R[b_i]) for b_i in B) == 1
        for v_i in V_ID
    ), name="(11)")

    m.addConstrs((
        (gb.quicksum(
            gb.quicksum(gb.quicksum(x[v_i, i_i, 0, b_i, r_i] for i_i in Pv[v_i]) for r_i in R[b_i]) for b_i in B) == 1)
        for v_i in V_ID
    ), name="(12)")

    m.addConstrs((
        (gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, j_i, l_i, b_i, r_i] for r_i in R[b_i]) for b_i in B) for l_i in
                     Pv[v_i] + [0]) <=
         gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for r_i in R[b_i]) for b_i in B) for i_i in
                     Pv[v_i] + [0]))
        for v_i in V_ID for j_i in Pv[v_i]
    ), name="(13)")

    m.addConstrs((
        (gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, l_i, j_i, b_i, r_i] for r_i in R[b_i]) for b_i in B) for l_i in
                     Pv[v_i] + [0]) <=
         gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, j_i, i_i, b_i, r_i] for r_i in R[b_i]) for b_i in B) for i_i in
                     Pv[v_i] + [0]))
        for v_i in V_ID for j_i in Pv[v_i]
    ), name="(14)")

    # m.addConstrs((
    #     (gb.quicksum(gb.quicksum(y[i_i, j_i, b_i, r_i] for j_i in P) for i_i in P) <= 1)
    #     for b_i in B for r_i in R[b_i]
    # ), name="(15.1)")

    m.addConstrs(((I_br[b_i, r_i] == 0) >> (y[i_i, j_i, b_i, r_i] + A[i_i, j_i] <= 1)for i_i in P if i_i != 0 for j_i in P if j_i !=0 for b_i in B for r_i in R[b_i]), name="(15.2.1)")
    m.addConstrs(
        ((I_br[b_i, r_i] == 1) >> (y[i_i, j_i, b_i, r_i] <= 1) for i_i in P if i_i != 0 for j_i in P if
         j_i != 0 for b_i in B for r_i in R[b_i]), name="(15.2.2)")
    m.addConstrs((z_BF[r_i, b_i] - model_index.Z2 <= M * I1_br[b_i, r_i] for b_i in B for r_i in R[b_i]), name="(15.3)")
    m.addConstrs((-z_BF[r_i, b_i] + model_index.Z2 + e <= M * (1 - I1_br[b_i, r_i]) for b_i in B for r_i in R[b_i]), name="(15.4)")
    m.addConstrs((-z_BF[r_i, b_i] + model_index.Z1 <= M * I2_br[b_i, r_i] for b_i in B for r_i in R[b_i]), name="(15.5)")
    m.addConstrs((z_BF[r_i, b_i] - model_index.Z1 + e <= M * (1 - I2_br[b_i, r_i]) for b_i in B for r_i in R[b_i]), name="(15.6)")
    m.addConstrs((I_br[b_i, r_i] <= I1_br[b_i, r_i] + I2_br[b_i, r_i] for b_i in B for r_i in R[b_i]), name="(15.7)")
    m.addConstrs((I_br[b_i, r_i] >= I1_br[b_i, r_i] for b_i in B for r_i in R[b_i]), name="(15.8)")
    m.addConstrs((I_br[b_i, r_i] >= I2_br[b_i, r_i] for b_i in B for r_i in R[b_i]), name="(15.9)")



    m.addConstrs((
        (gb.quicksum(y[i_i, i_i, b_i, r_i] for i_i in P) == 0)
        for b_i in B for r_i in R[b_i]
    ), name="(16)")

    m.addConstrs((
        (gb.quicksum(gb.quicksum(y[i_i, j_i, b_i, r_i] for j_i in P) for i_i in P) <= gb.quicksum(
            gb.quicksum(y[i_i, j_i, b_i, (r_i - 1)] for j_i in P) for i_i in P))
        for b_i in B for r_i in R[b_i] if r_i >= 2
    ), name="(17)")

    m.addConstrs((
        (gb.quicksum(y[j_i, l_i, b_i, r_i] for l_i in P) <= gb.quicksum(y[i_i, j_i, b_i, (r_i - 1)] for i_i in P))
        for b_i in B for r_i in R[b_i] if r_i >= 2 for j_i in P
    ), name="(18)")


    m.addConstrs((
        (gb.quicksum(y[i_i, 0, b_i, r_i] for i_i in P if i_i != 0) >=
         (gb.quicksum(gb.quicksum(y[i_i, j_i, b_i, (r_i - 1)] for j_i in P if j_i != 0) for i_i in P) - gb.quicksum(
             gb.quicksum(y[i_i, j_i, b_i, r_i] for j_i in P if j_i != 0) for i_i in P if i_i != 0)))
        for b_i in B for r_i in R[b_i] if r_i >= 2
    ), name="(19)")


    m.addConstrs((
        (gb.quicksum(y[0, j_i, b_i, 1] for j_i in P if j_i != 0) == gb.quicksum(
            gb.quicksum(y[i_i, j_i, b_i, 2] for j_i in P) for i_i in P))
        for b_i in B
    ), name="(20)")

    # m.addConstrs((
    #     (gb.quicksum(y[i_i, 0, b_i, 1] for i_i in P if i_i != 0) == 1)
    #     for b_i in B
    # ), name="(20.1)")

    m.addConstrs((
        (gb.quicksum(Nv[v_i] * x[v_i, i_i, j_i, b_i, r_i] for v_i in V_ID) <= model_index.Cb * y[i_i, j_i, b_i, r_i])
        for i_i in P for j_i in P for b_i in B for r_i in R[b_i]
    ), name="(21)")
    # m.addConstrs((
    #     (gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for v_i in V_ID) <= y[i_i, j_i, b_i, r_i])
    #     for i_i in P for j_i in P for b_i in B for r_i in R[b_i]
    # ), name="(21.1)")

    m.addConstrs((
        (z_BF[r_i, b_i] == z_BS[r_i, b_i] + gb.quicksum(
            gb.quicksum(tau[i_i, j_i] * y[i_i, j_i, b_i, r_i] for j_i in P) for i_i in P))
        for b_i in B for r_i in R[b_i]
    ), name="(22)")

    m.addConstrs((
        (z_BS[r_i, b_i] >= z_BF[(r_i - 1), b_i])
        for b_i in B for r_i in R[b_i] if r_i >= 2
    ), name="(23)")

    m.addConstrs((
        (z_BS[r_i, b_i] >= z_GA[v_i, i_i] + ts[v_i, i_i] - M * (
                1 - gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i] + [0])))
        for b_i in B for r_i in R[b_i] for v_i in V_ID for i_i in Pv[v_i]
    ), name="(24)")

    m.addConstrs((
        (z_BS[r_i, b_i] >= Te[v_i] - M * (1 - gb.quicksum(x[v_i, 0, j_i, b_i, r_i] for j_i in Pv[v_i])))
        for b_i in B for r_i in R[b_i] for v_i in V_ID
    ), name="(25)")

    # m.addConstrs((
    #     (z_GA[v_i, i_i] - TE <= M * L[v_i, i_i] + M * (gb.quicksum(1 - x[v_i, j_i, i_i, b_i, r_i] for j_i in Pv[v_i] + [0] for b_i in B for r_i in R[b_i])) )
    #     for v_i in V_ID for i_i in Pv[v_i]
    # ), name="(26)")
    m.addConstrs((
        (z_GA[v_i, i_i] - TE <= M * L[v_i, i_i] for v_i in V_ID for i_i in Pv[v_i])), name="(26)")

    m.addConstrs((
        L[v_i, 0] == 0 for v_i in V_ID), name="(26.1)")

    m.addConstrs((
        (-z_GA[v_i, i_i] + TE + e <= M * (1 - L[v_i, i_i]))for v_i in V_ID for i_i in Pv[v_i]), name="(27)")

    # m.addConstrs((((len(Pv[v_i]) - M * (1 - TC[v_i]))
    #              <= (gb.quicksum(gb.quicksum(gb.quicksum(gb.quicksum(x[v_i,i_i,j_i,b_i,r_i] for i_i in Pv[v_i] + [0])for r_i in R[b_i])for b_i in B)for j_i in Pv[v_i])))
    #               for v_i in V_ID), name="(27.1)")
    # m.addConstrs((((len(Pv[v_i]) + M * (1 - TC[v_i]))
    #                >= (gb.quicksum(gb.quicksum(gb.quicksum(gb.quicksum(x[v_i,i_i,j_i,b_i,r_i] for i_i in Pv[v_i] + [0])for r_i in R[b_i])for b_i in B)for j_i in Pv[v_i])))
    #               for v_i in V_ID), name="(27.2)")
    # m.addConstrs((((TC[v_i])
    #                == (gb.quicksum(gb.quicksum(gb.quicksum(gb.quicksum(x[v_i,i_i,j_i,b_i,r_i] for i_i in Pv[v_i] + [0])for r_i in R[b_i])for b_i in B)for j_i in Pv[v_i])))
    #               for v_i in V_ID), name="(27.2)")
    """
    m.addConstrs((TC[v_i, j_i] >=
                  1 + M * (gb.quicksum(gb.quicksum(gb.quicksum(x[v_i,i_i,j_i,b_i,r_i] for i_i in Pv[v_i] + [0])for r_i in R[b_i])for b_i in B) - len(Pv[v_i]))
                  + M * (gb.quicksum(gb.quicksum(x[v_i,j_i,0,b_i,r_i] for r_i in R[b_i])for b_i in B) - 1) for v_i in V_ID for j_i in Pv[v_i]), name="(27.1)")

    m.addConstrs((TC[v_i, j_i] * len(Pv[v_i]) + M * (gb.quicksum(gb.quicksum(x[v_i,j_i,0,b_i,r_i] for r_i in R[b_i])for b_i in B) - 1) <=
                  gb.quicksum(gb.quicksum(gb.quicksum(x[v_i,i_i,j_i,b_i,r_i] for i_i in Pv[v_i] + [0])for r_i in R[b_i])for b_i in B)
                  for v_i in V_ID for j_i in Pv[v_i]), name="(27.2)")
    """
    m.addConstrs((TC_V[v_i] >=
                  1 + M * (gb.quicksum(gb.quicksum(gb.quicksum(gb.quicksum(x[v_i,i_i,k_i,b_i,r_i] for i_i in Pv[v_i] + [0])for k_i in Pv[v_i])for r_i in R[b_i])for b_i in B) - len(Pv[v_i]))
                for v_i in V_ID), name="(28.1)")

    m.addConstrs((TC_V[v_i] * len(Pv[v_i]) <=
                  gb.quicksum(gb.quicksum(gb.quicksum(gb.quicksum(x[v_i,i_i,k_i,b_i,r_i] for i_i in Pv[v_i] + [0])for k_i in Pv[v_i])for r_i in R[b_i])for b_i in B)
                  for v_i in V_ID), name="(28.2)")
    m.addConstrs((TC[v_i, j_i] >= 1 + M * (gb.quicksum(gb.quicksum(x[v_i,j_i,0,b_i,r_i] for r_i in R[b_i])for b_i in B) - 1)
                  + M * (TC_V[v_i] - 1)for v_i in V_ID for j_i in Pv[v_i]), name="(28.3)")
    m.addConstrs((TC[v_i, j_i] <= M * gb.quicksum(gb.quicksum(x[v_i,j_i,0,b_i,r_i] for r_i in R[b_i])for b_i in B) for v_i in V_ID for j_i in Pv[v_i]),name="(28.4)")
    m.addConstrs((TC[v_i, j_i] <= M * TC_V[v_i] for v_i in V_ID for j_i in Pv[v_i]),name="(28.5)")

    # 辅助变量 L_TC
    m.addConstrs((L_TC[v_i, i_i] <= L[v_i, i_i] + TC[v_i, i_i] for v_i in V_ID for i_i in Pv[v_i]), name="(28.6)")
    m.addConstrs((L_TC[v_i, i_i] >= L[v_i, i_i] for v_i in V_ID for i_i in Pv[v_i]), name="(28.7)")
    m.addConstrs((L_TC[v_i, i_i] >= TC[v_i, i_i] for v_i in V_ID for i_i in Pv[v_i]), name="(28.8)")



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
        (z_GD[v_i, i_i] - z_GA[v_i, i_i] - ts[v_i, i_i] * gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i] + [0]) for r_i in R[b_i]) for b_i in B)
         - ts[v_i, i_i] * gb.quicksum(gb.quicksum(gb.quicksum(x[v_i, j_i, i_i, b_i, r_i] for j_i in Pv[v_i] + [0])for r_i in R[b_i]) for b_i in B) >= 0)
        for v_i in V_ID for i_i in Pv[v_i]
    ), name="(33)")

    # m.addConstrs((z_BS[r_i, b_i] >= z_GA[v_i, i_i] + ts[v_i, i_i] - M * (1 - gb.quicksum(x[v_i, i_i, j_i, b_i, r_i] for j_i in Pv[v_i]+[0]))
    #               for v_i in V_ID for b_i in B for r_i in R[b_i] for i_i in Pv[v_i]), name="(33)")

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
        m.write('./data/test_1_small_c4_1.MPS')
        print("写入测试模型1")
    else:
        m.write('./data/test_2_small_c4_1.MPS')
        print("写入测试模型2")

