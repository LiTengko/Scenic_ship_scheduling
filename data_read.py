# _*_ coding:utf-8 _*_
"""
@File     : data_read.py
@Project  : MIP_solver
@Time     : 2023/4/29 10:38
@Author   : Li D.K
@Contact  : lidengke@zju.edu.cn
@Software : PyCharm
@License  : (C)Copyright 2022 SRTP
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2023/4/29 10:38   Li D.K.      1.0         None
-----------------------------------------------------
Feature description：
定义了从数据表中读取数据的实现
"""

# import lib
import model_index
import os
import pandas as pd


def create_tau():
    """
    从 tau.csv中创建 multidict 变量
    其中键为(i,j),以0表示g；值为tau_ij
    tau_ij 以 tau[i,j]索引  arc为包含(i,j)的列表
    :return: multidict变量,路径arcs 和 时间tau_ij
    """
    file_path = os.path.join(model_index.output_folder, "tau.csv")
    if not os.path.exists(file_path):
        print("需要先生成tau.csv")
    else:
        # 读取数据表文件
        df = pd.read_csv(file_path)
        # 创建空字典
        dict_ij = {}
        # 遍历数据表，将每个(i,j)位置的值添加到字典中
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                key = (i, j)
                value = df.iloc[i, j]
                dict_ij[key] = value
        # 打印字典
        return dict_ij


def create_Nv_Te():
    """
    从 visitor.csv中创建 multidict 变量
    其中键为v_ID,两字典的值分别为Nv和TE,两者索引分别为 Nv[v_ID] TE[v_ID]
    :return: Nv,TE
    """
    file_path = os.path.join(model_index.output_folder, "visitor.csv")
    if not os.path.exists(file_path):
        print("需要先生成visitor.csv")
    else:
        # 读取 CSV 文件
        df = pd.read_csv(file_path)

        # 将 ID 列设置为数据帧的索引
        df.set_index('ID', inplace=True)

        # 创建 Nv 和 TE 字典
        Nv = df['NV'].to_dict()
        Te = df['TE'].to_dict()
    return Nv, Te


def create_Pv_ts():
    """
    从ts.csv生成字典变量PV和ts
    :return: 字典变量PV，ts；其中PV[v_ID]，ts[v_ID,p] (注意！ts中p不包含大门 0)
    """
    file_path = os.path.join(model_index.output_folder, "ts.csv")
    if not os.path.exists(file_path):
        print("需要先生成ts.csv")
    else:
        # 读取 CSV 文件
        data = pd.read_csv(file_path)
        # 根据给定的规则生成字典变量 PV
        Pv = {}
        ts = {}
        for index, row in data.iterrows():
            Pv[row['0']] = [idx for idx, value in enumerate(row) if value > 5 and idx != 0]  # 跳过 ID 列
            for i in range(1, model_index.P_NUM + 1):  # 从 1 到 P_NUM
                ts[row['0'], i] = row[i]
        return Pv, ts
