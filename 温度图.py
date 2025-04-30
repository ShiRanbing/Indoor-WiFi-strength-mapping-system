import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# 使用TkAgg后端
matplotlib.use('TkAgg')

# retrieve data
data = pd.read_excel('C:\\Users\\86185\\Desktop\\wifi强度2.xlsx', index_col=0)
data1 = data.values

# Creating Images
f, ax = plt.subplots()

# Definition to colour map wifi strength from red to green
colors = ["red", "yellow", "green"]  # Red -> Yellow -> Green
cmap_red_green = LinearSegmentedColormap.from_list("RedToGreen", colors)

# Heat mapping
im = ax.imshow(data1, cmap=cmap_red_green)

# Setting Axis Labels and Titles
ax.set_xlabel("Room length(m)", fontsize=12)
ax.set_ylabel("Room width(m)", fontsize=12)
ax.set_title("Indoor WiFi signal strength heat map(dBm)", fontsize=12)

# Setting the x-axis and y-axis scales and labels
ind = data.index  # Remove row index
objects = data.columns  # Taking out the column index
ax.set_xticks(ticks=np.arange(len(objects)), labels=objects, fontsize=12)  # Setting the x-axis value
ax.set_yticks(ticks=np.arange(len(ind)), labels=ind, fontsize=12)  # Setting the y-axis value

# Displaying values in a heat map
for i in range(len(ind)):
    for j in range(len(objects)):
        ax.text(j, i, (data1[i, j]), ha="center", va="center")  # 利用for循环将每一个向量的数值放到图中
# Adding a colour bar
plt.colorbar(mappable=im)
# Show image
plt.show()


