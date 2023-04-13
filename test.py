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



# 读取 CSV 文件
df = pd.read_csv('./data/visitor.csv')

# 将 ID 列设置为数据帧的索引
df.set_index('ID', inplace=True)

# 创建 Nv 和 TE 字典
Nv = df['NV'].to_dict()
TE = df['TE'].to_dict()
print(Nv)
print(TE)
