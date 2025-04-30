import sys
import os
import numpy as np
import pandas as pd
import matplotlib
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtWidgets, QtCore
from scipy.interpolate import griddata
from typing import Any  # 添加类型提示支持

matplotlib.use('Qt5Agg')

def resource_path(relative_path: str) -> str:
    """获取资源的绝对路径，打包后也能正确访问"""
    # 使用更安全的hasattr检查方式
    if getattr(sys, '_MEIPASS', None):
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class HeatmapCanvas(FigureCanvas):
    """Matplotlib 图像内嵌到Qt窗口的widget"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # 隐藏坐标轴
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.axes.axis('off')
        super().__init__(fig)
        self.setParent(parent)

class WiFiHeatmapApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WiFi信号热力图生成器")
        self.setGeometry(100, 100, 900, 700)

        # 组件
        self.uploadBtn = QtWidgets.QPushButton("上传Excel/CSV文件")
        self.noInterpBtn = QtWidgets.QPushButton("生成无插值热力图")
        self.interpBtn = QtWidgets.QPushButton("生成插值热力图")
        self.saveBtn = QtWidgets.QPushButton("导出当前热力图为图片")
        self.statusLabel = QtWidgets.QLabel("请选择WiFi信号强度数据文件。")
        self.canvas = HeatmapCanvas(self, width=8, height=5, dpi=100)

        # 布局
        vbox = QtWidgets.QVBoxLayout()
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.uploadBtn)
        hbox.addWidget(self.noInterpBtn)
        hbox.addWidget(self.interpBtn)
        hbox.addWidget(self.saveBtn)
        vbox.addLayout(hbox)
        vbox.addWidget(self.statusLabel)
        # self.statusLabel.setFixedHeight(40)
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)

        # 信号连接
        self.uploadBtn.clicked.connect(self.upload_data)
        self.noInterpBtn.clicked.connect(lambda: self.show_heatmap(interpolate=False))
        self.interpBtn.clicked.connect(lambda: self.show_heatmap(interpolate=True))
        self.saveBtn.clicked.connect(self.save_figure)

        # 数据
        self.df = None
        self.plot_type = None     # 'no_interp' or 'interp'

    def upload_data(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择数据文件",
                                                            "", "Excel Files (*.xlsx);;CSV Files (*.csv)")
        if not fileName:
            return
        try:
            if fileName.endswith('.xlsx'):
                self.df = pd.read_excel(fileName, index_col=0)
            elif fileName.endswith('.csv'):
                self.df = pd.read_csv(fileName, index_col=0)
            else:
                QtWidgets.QMessageBox.warning(self, "文件格式错误", "仅支持xlsx和csv文件")
                return
            self.statusLabel.setText(f"已加载文件：{os.path.basename(fileName)}，请生成热力图。")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "读取失败", f"读取文件失败：{e}")
            self.df = None

    def show_heatmap(self, interpolate=False):
        if self.df is None:
            QtWidgets.QMessageBox.warning(self, "未加载数据", "请先上传数据文件")
            return
        
        # 清除之前的绘图内容
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)  # 创建新的坐标轴
        
        # 获取数据值、行标签和列标签
        data = self.df.values  # 二维数组，存储信号强度值
        y_labels = self.df.index  # 行标签，通常表示y轴坐标(房间宽度)
        x_labels = self.df.columns  # 列标签，通常表示x轴坐标(房间长度)

        # 创建红黄绿渐变色配色方案
        colors = ["red", "yellow", "green"]
        cmap = LinearSegmentedColormap.from_list("RedToGreen", colors)
        
        if not interpolate:
            # 无插值热力图
            im = ax.imshow(data, cmap=cmap)  # 直接显示原始数据
            
            # 在每个单元格中心添加数值标签
            for i in range(len(y_labels)):  # 遍历行(y轴)
                for j in range(len(x_labels)):  # 遍历列(x轴)
                    v = data[i, j]
                    # 在(j,i)位置添加文本，j对应x轴，i对应y轴
                    ax.text(j, i, str(v), ha='center', va='center', fontsize=9, color='black')
            self.plot_type = 'no_interp'
        else:
            # 插值热力图处理
            # 创建网格坐标系统
            x = np.arange(len(x_labels))  # x轴坐标(0,1,2,...)
            y = np.arange(len(y_labels))  # y轴坐标(0,1,2,...)
            xx, yy = np.meshgrid(x, y)  # 生成网格坐标
            
            # 准备插值数据
            points = np.column_stack((xx.flatten(), yy.flatten()))  # 所有数据点的(x,y)坐标
            values = data.flatten()  # 对应的信号强度值
            
            # 创建更密集的网格用于插值(100x100)
            grid_x, grid_y = np.meshgrid(
                np.linspace(0, len(x_labels)-1, 100),  # x轴插值点
                np.linspace(0, len(y_labels)-1, 100)   # y轴插值点
            )
            
            # 使用三次样条插值
            grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')
            im = ax.imshow(grid_z, cmap=cmap, 
                          extent=(0, len(x_labels)-1, len(y_labels)-1, 0))  # 设置坐标范围
            self.plot_type = 'interp'

        # 设置坐标轴标签(边框坐标)
        ax.set_xlabel("Room length(m)", fontsize=12)  # x轴标签
        ax.set_ylabel("Room width(m)", fontsize=12)  # y轴标签
        ax.set_title("Indoor WiFi signal strength heat map(dBm)", fontsize=12)  # 标题
        
        # 设置刻度位置和标签(边框坐标)
        ax.set_xticks(np.arange(len(x_labels)))  # x轴刻度位置
        ax.set_xticklabels(x_labels, fontsize=10)  # x轴刻度标签
        ax.set_yticks(np.arange(len(y_labels)))  # y轴刻度位置
        ax.set_yticklabels(y_labels, fontsize=10)  # y轴刻度标签
        
        # 添加颜色条(右侧的色标)
        self.canvas.figure.colorbar(im, ax=ax)
        
        # 隐藏坐标轴边框(但保留标签和刻度)
        self.canvas.axes.axis('off')
        
        # 重绘画布
        self.canvas.draw()

        if interpolate:
            self.statusLabel.setText("已显示插值热力图，可导出图片。")
        else:
            self.statusLabel.setText("已显示无插值热力图，可导出图片。")

    def save_figure(self):
        if self.df is None or self.plot_type is None:
            QtWidgets.QMessageBox.warning(self, "没有热力图", "请先生成热力图")
            return
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "保存热力图", "",
                                                            "PNG Files (*.png);;JPG Files (*.jpg);;PDF Files (*.pdf)")
        if fileName:
            self.canvas.figure.savefig(fileName)
            self.statusLabel.setText(f"已保存图片到: {fileName}")

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = WiFiHeatmapApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()