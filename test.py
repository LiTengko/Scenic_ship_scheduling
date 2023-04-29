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
import pandas as pd
import gurobipy as gb
import os
import model_index
from gurobipy import GRB
X = [
    [ [1,0,0,0,0,0,0,0,0], [2,0,0,0,0,0,0,0,0], [3,0,0,0,0,0,0,0,0] ],
    [ [1,1,0,0,0,0,0,0,0], [2,2,0,0,0,0,0,0,0], [3,3,0,0,0,0,0,0,0] ],
    [ [1,0,0,0,0,0,0,0,0], [2,0,0,0,0,0,0,0,0], [3,0,0,0,0,0,0,0,0] ],
]
v_m = 2  # 筛选条件：元素第1位置等于 v_m
res = [elem for lst in X for elem in lst if elem[0] == v_m and elem[1] == 0][0]

print(res)


