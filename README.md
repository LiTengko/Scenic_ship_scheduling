Copyright &copy; 2023，Li Tengko [<img src="https://cdn.jsdelivr.net/gh/LiTengko/Picgo_Pictures@main/img/GitHub-Mark.png" alt="GitHub" width="30"/>](https://github.com/LiTengko/MIP_solver)
## 前述章节对应的代码实现：
- 3节混合整数规划主要由model_generate.py实现，model_solve.py完成模型求解；
- 4.1节数据生成主要由data_generate.py实现；
- 4.2节，5.4节小规模数值实验原始结果记录于data_log.md当中；
- 5.4节数据集合存储在orign_data文件当中，数据集文件命名与文中相同；
## 复现本项目的主要流程：
	1.配置Python3.9环境以及gurobipy工具包(version 10.0.1)；
	2.克隆本项目到本地；
	3.设置model_index.py当中的各项参数；
	4.运行data_generate.py生成数据，所生成的数据在data文件夹下；若需复现本文结果，请直接在orign_data中找到对应数据集文件，替换data文件夹内数据表即可；
	5.在model_generate.py中设置一票制、两部制，运行后即在data文件夹下生成.MPS文件；
	6.运行model_solve.py读取.MPS文件，调用求解器求解混合整数规划模型；可在运行前设置求解参数；
	7.在ts_model.py中设置禁忌搜索参数及所需求解的票制类型，运行即是使用禁忌搜索算法求解，数据源为data文件夹下数据表；
