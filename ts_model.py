# _*_ coding:utf-8 _*_
"""
@File     : ts_model.py
@Project  : MIP_solver
@Time     : 2023/5/2 20:46
@Author   : Li D.K
@Contact  : lidengke@zju.edu.cn
@Software : PyCharm
@License  : (C)Copyright 2022 SRTP
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2023/5/2 20:46   Li D.K.      1.0         None
-----------------------------------------------------
Feature description：
"""

# import lib
# import lib
import model_index
import data_read
import random
import gurobipy as gb

# 读取数据表中的信息
tau = data_read.create_tau()  # tau[i,j]
Pv, ts = data_read.create_Pv_ts()  # Pv[v], ts[v, i]
Nv, Te = data_read.create_Nv_Te()  # Nv[v], Te[v]


def TSP_optimize(v_id):
    # 如果只有一个景点，不能求解，直接返回
    if len(Pv[v_id]) <= 1:
        return [0] + Pv[v_id] + [0]
    else:
        # 创建模型
        m = gb.Model()
        # 关闭计算详情的输出
        m.setParam('OutputFlag', 0)

        # 定义变量
        x = {}
        for i in Pv[v_id]+[0]:
            for j in Pv[v_id]+[0]:
                x[i, j] = m.addVar(vtype=gb.GRB.BINARY, name='x')

        # 定义目标函数
        obj = gb.quicksum(tau[i, j] * x[i, j] for i in Pv[v_id] + [0] for j in Pv[v_id] + [0])
        m.setObjective(obj, gb.GRB.MINIMIZE)

        # 定义约束条件
        for i in Pv[v_id]:
            m.addConstr(gb.quicksum(x[i, j] for j in Pv[v_id] + [0] if j != i) == 1)
            m.addConstr(gb.quicksum(x[j, i] for j in Pv[v_id] + [0] if j != i) == 1)

        for i in Pv[v_id] + [0]:
            for j in Pv[v_id] + [0]:
                if i != j:
                    m.addConstr(x[i, j] + x[j, i] <= 1)

        for i in Pv[v_id]:
            m.addConstr(gb.quicksum(x[i, j] for j in Pv[v_id] + [0] if j != i) +
                        gb.quicksum(x[j, i] for j in Pv[v_id] + [0] if j != i) == 2)
        # 游团从0出发
        m.addConstr(gb.quicksum(x[0, j] for j in Pv[v_id]) == 1)

        # 游团最终返回0
        m.addConstr(gb.quicksum(x[i, 0] for i in Pv[v_id]) == 1)
        # 求解
        m.optimize()

        # 提取结果
        visit = [0]  # 起点为 0
        v_index = 0

        i = 0
        while True:
            for j in Pv[v_id] + [0]:
                if x[i, j].x > 0.5:
                    visit.append(j)
                    i = j
                    break
            if i == 0:
                break



        return visit

X = {}
for v_i in range(1, model_index.V_NUM + 1):
    X[v_i] = TSP_optimize(v_i)

print(X)