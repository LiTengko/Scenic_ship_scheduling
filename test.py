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
import heuristics_model

X = heuristics_model.initial_v_i_j()

# print([lst for lst in X if lst[0] == 2 and lst[1] == 0][0][3])
# print([lst for lst in X if lst[3] == 1 and lst[4] == -1][0])

# v_m = 2  # 筛选条件：元素第1位置等于 v_m
# res = [elem for lst in X for elem in lst if elem[0] == v_m and elem[1] == 0][0]

B, Y = heuristics_model.initial_b_r1_z(X)

print(B, Y)


