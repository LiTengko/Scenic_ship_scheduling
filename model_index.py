# _*_ coding:utf-8 _*_
"""
@File     : model_index.py
@Project  : MIP_solver
@Time     : 2023/4/24 13:32
@Author   : Li D.K
@Contact  : lidengke@zju.edu.cn
@Software : PyCharm
@License  : (C)Copyright 2022 SRTP
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2023/4/24 13:32   Li D.K.      1.0         None
-----------------------------------------------------
Feature description：
Specifies all the coefficients that are useful in the model
"""
'''
静态变量指定
P_NUM 内部景点数
V_NUM 游团数量
B_NUM 游船数量
Cb    游船载客量
R_MAX 每船最大行程数
'''
# import lib
import os

P_NUM = 7
V_NUM = 50
B_NUM = 30
Cb = 20
R_MAX = 15
# 指定系数
P_all_a = 80  # 一票制票价
P_all_b = 50  # 两部制票价
pm = ({1: 10, 2: 15, 3: 10, 4: 15, 5: 10, 6: 15, 7: 10})  # 两部制下各景点票价
c1 = 3   # 票价系数c1
c2 = 1   # 固定成本系数c2
c3 = 2   # 行驶成本系数c3
c4 = 1   # 等待成本系数c4

TE = 570  # 设置最晚入园时间为16:30,计算与7：00的差值为570 min  注意！设置TE时应小于游客入园时间TE

output_folder = "./data"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
