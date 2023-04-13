# _*_ coding:utf-8 _*_
"""
@File     : data_read_var_generate.py
@Project  : MIP_solver
@Time     : 2023/4/13 13:22
@Author   : Li D.K
@Contact  : lidengke@zju.edu.cn
@Software : PyCharm
@License  : (C)Copyright 2022 SRTP
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2023/4/13 13:22   Li D.K.      1.0         None
-----------------------------------------------------
Feature description：
根据csv中的变量创建对应格式的变量
并创建模型，添加变量
"""

# import lib
import pandas as pd
import gurobipy as gb
import os
import data_generate


def create_tau():
    """
    从 tau.csv中创建 multidict 变量
    其中键为(i,j),以0表示g；值为tau_ij
    :return: multidict变量,路径arcs 和 时间tau_ij
    """
    file_path = os.path.join(data_generate.output_folder, "tau.csv")
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
        arcs, tau_ij = gb.multidict(dict_ij)
        return arcs, tau_ij

def  create_Nv_TE():
    """
    从 visitor.csv中创建 multidict 变量
    其中键为v_ID,两字典的值分别为Nv和TE
    :return: Nv,TE
    """
    file_path = os.path.join(data_generate.output_folder, "visitor.csv")
    if not os.path.exists(file_path):
        print("需要先生成visitor.csv")
    else:
        # 读取 CSV 文件
        df = pd.read_csv(file_path)

        # 将 ID 列设置为数据帧的索引
        df.set_index('ID', inplace=True)

        # 创建 Nv 和 TE 字典
        Nv = gb.multidict(df['NV'].to_dict())
        TE = gb.multidict(df['TE'].to_dict())
    return Nv, TE




if not os.path.exists(data_generate.output_folder):
    print("需要先运行data_generate.py")
else:
    #  代码主体

    # 由数据表生成multidict变量
    arcs, tau_ij = create_tau()
    # print(arcs)
    # print(tau_ij)
    Nv, TE = create_Nv_TE()
    # print(Nv)
    # print(TE)

    # 生成tuplelist变量
    v_ID = gb.tuplelist([x for x in range(1, data_generate.V_NUM+1)])
    P = gb.tuplelist([x for x in range(0, data_generate.P_NUM)])
    b = gb.tuplelist([x for x in range(1, data_generate.B_NUM+1)])
    R = gb.tuplelist([x for x in range(1, data_generate.R_MAX+1)])

    m = gb.Model("test1")
    x = m.addVars(v_ID, arcs, b, R, name="x")
    m.write("./data/test1.lp")
