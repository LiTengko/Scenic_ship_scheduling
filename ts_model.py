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
    """
    使用 TSP 求解得到最优环游
    :param v_id: 游团编号
    :return: 该游团起终点为 0 的环游顺序
    """
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
        for i in Pv[v_id] + [0]:
            for j in Pv[v_id] + [0]:
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


def X_split(X):
    """
    将游客游览集合进行拆分
    :param X: 游团环游顺序的字典变量
    :return: 经拆分后的字典变量
    """
    x_tour = []
    for key, value in X.items():
        for i in range(0, len(value) - 1):
            visit_list = []
            visit_list.append(key)  # v
            visit_list.append(value[i])  # i
            visit_list.append(value[i + 1])  # j
            if i == 0:
                visit_list.append(Te[key])  # z^GD
            else:
                visit_list.append(-1)
            visit_list.append(-1)  # z^GA
            visit_list.append(-1)  # r
            x_tour.append(visit_list)

    return x_tour


def rough_value(X, type = None):
    """
    对环游的值进行粗略估计
    :param X: 输入的游客环游集合
    :param type: 1，一票制；2，两部制
    :return: 该环游对应的粗略值
    """
    # 首先对输入的所有环游进行拆分
    x_tour = X_split(X)  # x[v, i, j, z^GD, z^GA, r(-1 or 1)]
    b_num = 0  # 驳船总数
    B = []  # 驳船集合
    wait_total = 0  # 总等待时间

    # 对上述行程进行规划分配
    while all(elem[5] != -1 for elem in x_tour):  # 当有行程没有被规划时，执行以下
        # 找到行程未分配中最早的团
        v_index = 0
        early_time = min([x_tour[i][3] for i in range(len(x_tour)) if x_tour[i][3] == -1])
        for i in range(len(x_tour)):
            if x_tour[i][5] == -1 and x_tour[i][3] == early_time:
                v_index = i

        # 获得该团的信息
        v_i = x_tour[v_index][1]  # 出发点
        v_j = x_tour[v_index][1]  # 终点
        v_z_GD = x_tour[v_index][3]  # 预期出发时间
        # 最终找到的船编号为b_id, 终点为b_j
        b_id = 1
        cost = 0
        b_j = 0
        b_z_BF = 0
        add_flag = 0  # 用于新增驳船

        # 决策使用哪一条驳船接驳
        if b_num == 0:  # 初始化
            b_num += 1
            b_id = b_num
            b_j = 0
            b_list = [b_num, v_i, v_j, v_z_GD, v_z_GD]  # [b_i, i, j, z^BS, z^BF]  此时视驳船出发为到达大门时间
            B.append(b_list)
        else:  # 集合中查找

            for b in range(b_num):  # 对每一艘驳船进行计算
                # 找到b的最大z_BF和其对应的终点j
                b_z_BF_temp = 0
                j_temp = 0
                for b_list in B:
                    if b_list[0] == b:
                        if b_list[4] > b_z_BF_temp:
                            b_z_BF_temp = b_list[4]
                            j_temp = b_list[2]

                # 计算成本
                cost_temp = model_index.c4 * abs(b_z_BF_temp + tau[v_i, j_temp] - v_z_GD) + model_index.c3 * tau[v_i, j_temp]  # 等待成本 + 行驶成本
                # 若变量为0进行初始化
                if cost == 0:
                    cost = cost_temp
                    b_id = b
                    b_j = j_temp
                    b_z_BF = b_z_BF_temp

                # 若变量不为0，与之前的变量比大小
                else:
                    if cost < cost_temp:
                        # If 比之前的小，更新cost，并记录b_id j_temp
                        cost = cost_temp
                        b_id = b
                        b_j = j_temp
                        b_z_BF = b_z_BF_temp

            # 核算再添加一艘船的成本
            cost_add = model_index.c3 * tau[v_i, 0] + model_index.c2 * 1 / (0.5 * model_index.R_MAX)  # 行驶成本 + 船使用成本(均摊到最大行程的 1/2)
            if cost_add < cost:
                b_num += 1
                b_id = b_num
                b_j = 0
                add_flag = 1

            # 判断是否要加入空程
            if add_flag == 1:
                add_flag = 0
                b_list = [b_id, 0, v_i, v_z_GD - tau[0, v_i], v_z_GD]  # [b_i, i, j, z^BS, z^BF]  此时视驳船出发为到达大门时间
                B.append(b_list)
            else:
                if v_i != b_j:
                    b_list = [b_id, b_j, v_i, b_z_BF, b_z_BF + tau[v_i, b_j]]  # [b_i, i, j, z^BS, z^BF]

        # 驳船安排好后，考虑是否两者打包一起出游

        # 找到所有同程的游团，并将其按照出发时间排列
        same_trip = []
        for x_list in x_tour:
            if x_list[1] == v_i and x_list[2] == v_j and x_list[0] != v_index:
                same_trip.append(x_list)

        if same_trip:
            sorted_same_trip = sorted(same_trip, key=lambda x: x[3])

        else:
            # 没有同行的团，则仅考虑单独出行
            wait_total += abs(B[-1][4] + tau[b_j, v_i] - v_z_GD)  # 索引最后一个元素
            # 实际出发时间
            v_z_GD = max(B[-1][4] + tau[b_j, v_i], v_z_GD)
            # 实际到达时间
            v_z_GA = v_z_GD + tau[v_i, v_j]
            v_z_GD_next = v_z_GA + ts[v_index, v_j]
            # 在写入之前加入对是否超时返回的判断

            # 对该游团的行程进行写入
            for index in range(len(x_tour)):
                if x_tour[index][0] == v_index and x_tour[index][1] == v_i:
                    x_tour[index][4] = v_z_GA
                    x_tour[index][5] = 1
                if x_tour[index][0] == v_index and x_tour[index][1] == v_j:
                    x_tour[index][3] = v_z_GD_next
            # 对驳船行程进行写入
            B.append([b_id, v_i, v_j, v_z_GD, v_z_GA])



# 生成初始化的字典变量
X = {}
for v_i in range(1, model_index.V_NUM + 1):
    X[v_i] = TSP_optimize(v_i)

print(X)
x_tour = X_split(X)
print(x_tour)
