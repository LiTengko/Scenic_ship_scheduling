# _*_ coding:utf-8 _*_
"""
@File     : heuristics_model.py
@Project  : MIP_solver
@Time     : 2023/4/29 9:16
@Author   : Li D.K
@Contact  : lidengke@zju.edu.cn
@Software : PyCharm
@License  : (C)Copyright 2022 SRTP
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2023/4/29 9:16   Li D.K.      1.0         None
-----------------------------------------------------
Feature description：
使用启发式算法来解决这一问题
"""

# import lib
import model_index
import data_read
import random

# 读取数据表中的信息
tau = data_read.create_tau()  # tau[i,j]
Pv, ts = data_read.create_Pv_ts()  # Pv[v], ts[v, i]
Nv, Te = data_read.create_Nv_Te()  # Nv[v], Te[v]


def prob(z_GD, z_BS):
    """
    根据两时间差依概率返回判断结果
    :param z_GD: 游团出发时间
    :param z_BS: 驳船行程开始时间
    :return: 1，选择改行程；0，不选择该行程
    """
    p = 0.9 - (abs(z_GD - z_BS) / 120) * 0.9
    p = max(p, 0)  # 保证概率为正
    if random.random() < p:
        return 1
    else:
        return 0


def trip_is_not_assigned(i_start, X):
    '''
    判断X中起始点为i的旅行团是否还有没有被安排行程的
    :param i_start: 起始点
    :param X: 决策变量集合
    :return: 还没有被安排的景点,list类型，若为空则表明都安排
    '''
    v_not = []
    for element in X:
        if element[1] == i_start and element[3] == -1:
            v_not.append(element[0])
    return v_not


def initial_v_i_j():
    """
    生成初始环游，仅包含景点和景点环游，其余位置为-1
    :return: list变量X X[i]结构为(v, i, j, b, r, z_GD, z_GA, z_BS, z_BF)
    """
    X = []
    for v_i in range(1, model_index.V_NUM + 1):
        # 选择需要排列的变量数量（最少为1个，最多为全部）
        num = random.randint(1, len(Pv[v_i]))
        # 随机选择 num 个变量并进行随机排列
        travel_list = random.sample(Pv[v_i], num)
        random.shuffle(travel_list)
        # 环游首尾添加大门
        travel_list.insert(0, 0)
        travel_list.append(0)
        for i in range(0, len(travel_list) - 1):
            v_list = [-1] * 9  # 生成一个8个元素均为0的列表
            v_list[0] = v_i  # 设置第1个位置为 v_i
            v_list[1] = travel_list[i]  # 设置第2个位置为 travel_list 的第1个元素
            v_list[2] = travel_list[i + 1]  # 设置第3个位置为 travel_list 的第2个元素
            X.append(v_list)
    return X


def initial_b_r_z(X):
    # 初始化
    B_max = 1
    r = 1
    while True:  # 该循环对 r 进行迭代
        # 以下是对 r = 1 初始
        if r == 1:
            b = 1  # 初始化驳船数
            while True:  # 该循环对 b 进行迭代
                C = 0  # 初始化载客数
                flag_fist = 0  # 标志其为该船第一个载的行程
                select_list = list(range(1, model_index.V_NUM + 1))
                random.shuffle(select_list)
                for v_m in select_list:
                    # 按照其时间决策是否要对其分配行程
                    if random.random() < (1 - Te[v_m] / 600):
                        # 对其分配行程
                        pass
                    else:
                        # 不分配行程，找到该游团，对其进行标记
                        for i_i in range(len(X)):
                            trip = X[i_i]
                            if trip[0] == v_m and trip[1] == 0:  # 选择v_m 从 0 出发的行程
                                # 标记 b r
                                trip[3] = 0
                                trip[4] = 0
                                # 计算时间
                                z_GD = Te[v_m]  # 从 0 出发时间
                                # 写入时间
                                trip[5] = z_GD
                                # 将数据写入
                                X[i_i] = trip
                        continue  # 后续不再对该团进行判断

                    # 判断是否超载, 超载终止，后面的团也不能载
                    if C + Nv[v_m] > model_index.Cb:
                        break
                    # 如果没超载，执行后续
                    if flag_fist == 0 and [lst for lst in X if lst[0] == v_m and lst[1] == 0][0][3] == -1:  # 如果 v_m 是第一个元素，且还未安排行程安排其上船
                        flag_fist = 1
                        # 游客人数加入容量
                        C += Nv[v_m]
                        for i_i in range(len(X)):
                            trip = X[i_i]
                            if trip[0] == v_m and trip[1] == 0:  # 选择v_m 从 0 出发的行程
                                # 标记 b r
                                trip[3] = b
                                trip[4] = r
                                # 计算时间
                                z_GD = Te[v_m]  # 从 0 出发时间
                                z_BS = z_GD
                                z_BF = z_BS + tau[0, trip[2]]
                                z_GA = z_BF
                                # 写入时间
                                trip[5] = z_GD
                                trip[6] = z_GA
                                trip[7] = z_BS
                                trip[8] = z_BF
                            # 将数据写入
                            X[i_i] = trip
                    elif [lst for lst in X if lst[0] == v_m and lst[1] == 0][0][3] != -1:  # 如果 v_m 行程已经有安排(论不到该船)
                        pass
                    elif flag_fist != 0 and [lst for lst in X if lst[0] == v_m and lst[1] == 0][0][
                        3] == -1:  # v_m 已经不是第一程了，并且该行程没被安排
                        # 找到(b,r)已有的行程参数

                        trip_1 = [lst for lst in X if lst[3] == b and lst[4] == r][0]
                        # 判断两者目的地是否相同
                        if ([lst for lst in X if lst[0] == v_m and lst[1] == 0][0][2] == trip_1[2]) and \
                                ([lst for lst in X if lst[0] == v_m and lst[1] == 0][0][3] == -1):  # j相同且没被选择过
                            # 如果相同按概率判断是否上船
                            z_GD = Te[v_m]
                            z_BS = trip_1[7]  # 获得之前的z_BS
                            if prob(z_GD, z_BS) == 1:  # 允许该团上船
                                # 游客人数加入容量
                                C += Nv[v_m]
                                # 将出发时间统一为大者
                                z_BS = max(z_BS, z_GD)
                                z_GD = z_BS
                                # 标记该团的时间
                                for i_i in range(len(X)):
                                    trip = X[i_i]
                                    # 计算时间
                                    z_BF = z_BS + tau[0, trip[2]]
                                    z_GA = z_BF
                                    if trip[0] == v_m & trip[1] == 0:  # 选择v_m 从 0 出发的行程
                                        # 标记 b r
                                        trip[3] = b
                                        trip[4] = r
                                    if trip[3] == b & trip[4] == r:  # 选择所有的行程(b,r)
                                        # 写入时间
                                        trip[5] = z_GD
                                        trip[6] = z_GA
                                        trip[7] = z_BS
                                        trip[8] = z_BF
                                    # 将数据写入
                                    X[i_i] = trip

                            else:  # 不允许该团上船
                                pass

                v_not = trip_is_not_assigned(0, X)
                # 如果 v_not 为空，即所有均已分配行程或已经pass，则说明 r = 1已经全部分配，结束迭代
                if len(v_not) == 0:
                    r = r + 1
                    B_max = b
                    break
                else:
                    # 如果非空，设置有80%概率对b进行迭代，20%概率等待后面行程分配
                    if random.random() < 0.8:
                        b = b + 1
                    else:
                        r = r + 1
                        B_max = b
                        break

        # 以下是对 r 的迭代
        else:
            # 判断解内是否还有行程没有分配的
            if [lst for lst in X if lst[0] == 1 or lst[1] == 0][0][3] == -1:
                r = r + 1
                # 添加行程，对其进行分配
                b_list = list(range(1, B_max + 1))
                random.shuffle(b_list)
                # 依次对(b,r)的行程进行判断和分配
                for b_i in b_list:
                    trip_r_1 = [lst for lst in X if lst[3] == b_i and lst[4] == r - 1][0]

            else:
                # 跳出，结束对 r 的迭代
                break

    return B_max, r, X
