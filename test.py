import numpy as np
import random
import copy

# 生成距离矩阵
distances = np.array([
    [0, 10, 20, 30, 40],
    [10, 0, 15, 25, 35],
    [20, 15, 0, 10, 20],
    [30, 25, 10, 0, 10],
    [40, 35, 20, 10, 0]
])

n_cities = len(distances)
max_iterations = 1000
tabu_list_size = 20
freq_weight = 0.1  # 频率信息权重

# 计算路径长度
def path_length(path, distances):
    length = 0
    for i in range(len(path) - 1):
        length += distances[path[i]][path[i + 1]]
    length += distances[path[-1]][path[0]]
    return length

# 生成初始解
current_path = list(range(n_cities))
random.shuffle(current_path)
best_path = copy.deepcopy(current_path)

# 初始化禁忌表
tabu_list = []

# 初始化边使用频率矩阵
edge_frequency = np.zeros((n_cities, n_cities))

for iteration in range(max_iterations):
    # 邻域搜索
    candidates = []
    for i in range(1, n_cities - 1):
        for j in range(i + 1, n_cities):
            new_path = copy.deepcopy(current_path)
            new_path[i], new_path[j] = new_path[j], new_path[i]
            candidates.append((i, j, new_path))

    # 更新边使用频率
    for i in range(n_cities - 1):
        edge_frequency[current_path[i]][current_path[i + 1]] += 1
        edge_frequency[current_path[i + 1]][current_path[i]] += 1
    edge_frequency[current_path[-1]][current_path[0]] += 1
    edge_frequency[current_path[0]][current_path[-1]] += 1

    # 按照路径长度和边使用频率排序候选解
    candidates.sort(key=lambda x: path_length(x[2], distances) + freq_weight * edge_frequency[x[2][x[0]]][x[2][x[1]]])

    # 选择非禁忌的最优解，或者在特殊条件下选择禁忌解
    for i, j, new_path in candidates:
        if (i, j) not in tabu_list:
            current_path = new_path
            tabu_list.append((i, j))
            break

    # 更新最优解
    if path_length(current_path, distances) < path_length(best_path, distances):
        best_path = copy.deepcopy(current_path)

    # 禁忌表溢出策略
    if len(tabu_list) > tabu_list_size:
        tabu_list.pop(0)

print("Best path:", best_path)
print("Best path length:", path_length(best_path, distances))
