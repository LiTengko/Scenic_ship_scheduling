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

P_NUM = 4
V_NUM = 5
B_NUM = 3
Cb = 20
R_MAX = 10


output_folder = "./data"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
