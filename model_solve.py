# _*_ coding:utf-8 _*_
"""
@File     : model_solve.py
@Project  : MIP_solver
@Time     : 2023/4/18 9:37
@Author   : Li D.K
@Contact  : lidengke@zju.edu.cn
@Software : PyCharm
@License  : (C)Copyright 2022 SRTP
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2023/4/18 9:37   Li D.K.      1.0         None
-----------------------------------------------------
Feature description：
"""

# import lib
import gurobipy as gp

# 读取 MPS 文件并创建 Gurobi 模型对象
model = gp.read("./data/price_1_small.MPS")

# 对模型进行求解
model.optimize()

# 输出变量的解值
for v in model.getVars():
    if (v.x - 0) != 0:
        print(f"{v.varName}: {v.x}")
