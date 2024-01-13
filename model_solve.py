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
Solve the model and give the results for both cases
"""

# import lib
import gurobipy as gp
from threading import Thread

# 读取 MPS 文件并创建 Gurobi 模型对象
import model_generate

model1 = gp.read("./data/test_1_small_c4_1.MPS")
model2 = gp.read("./data/test_2_small_c4_1.MPS")


# 创建模型求解线程
def worker(model):
    # 设置模型参数
    # 参数自动调优
    # model.resetParams()
    # model.params.TuneTimeLimit = 100
    # model.tune()
    # model.setParam('NoRelHeurTime', 300)

    # 设置最大求解时间
    # model.Params.TimeLimit = 1200  # s
    # model.Params.Presolve = 2
    # model.params.Cuts = 3
    # model.Params.Aggregate = 2


    # 可设置迭代中使用启发式模式
    # model.setParam('Heuristics', 1)
    # model.setParam('HeuristicsMode', 0)
    # model.setParam('HeuristicsFreq', 1000)

    # model.Params.MIPFocus = 3
    # 在模型中使用回调函数
    # model.setParam('LazyConstraints', 1)
    # model._callback = model_generate.mycallback
    # model.optimize(model_generate.mycallback)
    model.optimize()

    # 输出变量的解值
    for v in model.getVars():
        if (v.x - 0) != 0:
            print(f"{v.varName}: {v.x}")



# 创建两个线程分别运行两个模型
thread1 = Thread(target=worker, args=(model1,))
thread2 = Thread(target=worker, args=(model2,))

# 启动线程1
print("\033[33m===================================================================\033[0m")
print("\033[33m=                        以下结果为 price1:                         =\033[0m")
print("\033[33m===================================================================\033[0m")
thread1.start()
# 等待线程1结束
thread1.join()


# # 启动线程2
# print("\033[33m===================================================================\033[0m")
# print("\033[33m=                        以下结果为 price2:                         =\033[0m")
# print("\033[33m===================================================================\033[0m")
# thread2.start()
# # 等待线程2结束
# thread2.join()





