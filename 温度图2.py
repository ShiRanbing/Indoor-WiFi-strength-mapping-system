import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import griddata

# 使用TkAgg后端
matplotlib.use('TkAgg')

# 读取数据
data = pd.read_excel('C:\\Users\\86185\\Desktop\\wifi强度2.xlsx', index_col=0)
data1 = data.values

# Get the grid coordinates of the original data
ind = data.index  # Row index (y-coordinate)
objects = data.columns  # Column index (x-coordinate)
x = np.arange(len(objects))  # Column indexes are converted to x-coordinates
y = np.arange(len(ind))  # Row indexes are converted to y-coordinates
xx, yy = np.meshgrid(x, y)  # Generate grid coordinates

# Generation of interpolated dense grids
grid_x, grid_y = np.meshgrid(
    np.linspace(0, len(objects) - 1, 100),  # 在x方向上生成100个点
    np.linspace(0, len(ind) - 1, 100)  # 在y方向上生成100个点
)

# 使用 griddata 进行插值
points = np.column_stack((xx.ravel(), yy.ravel()))  # 已知点的坐标
values = data1.ravel()  # 已知点的值
grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')  # 插值方法：cubic

# 创建图像
f, ax = plt.subplots()

# 定义从红色到绿色的颜色映射
colors = ["red", "yellow", "green"]
cmap_red_green = LinearSegmentedColormap.from_list("RedToGreen", colors)

# 绘制插值后的热力图
im = ax.imshow(grid_z, cmap=cmap_red_green, extent=(0, len(objects) - 1, len(ind) - 1, 0))

# 设置坐标轴标签和标题
ax.set_xlabel("Room length(m)", fontsize=12)
ax.set_ylabel("Room width(m)", fontsize=12)
ax.set_title("Indoor WiFi signal strength heat map(dBm)", fontsize=12)

# 设置x轴和y轴的刻度和标签
ax.set_xticks(ticks=np.arange(len(objects)), labels=objects, fontsize=12)  # 设置x轴的数值
ax.set_yticks(ticks=np.arange(len(ind)), labels=ind, fontsize=12)  # 设置y轴的数值

# 添加颜色条
plt.colorbar(mappable=im)

# 显示图像
plt.show()