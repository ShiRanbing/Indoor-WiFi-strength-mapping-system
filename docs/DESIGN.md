# 系统设计与代码导读

[返回项目首页](../README.md)

## 数据流

| 阶段 | 输入 | 处理 | 输出 |
| --- | --- | --- | --- |
| ESP32-S3 固件 | 指定 Wi-Fi 网络 | 连接、RSSI 采样、批次平均 | LCD 显示和串口数据行 |
| Python 记录器 | `RAW` / `AVG` 数据行 | 解析并附加电脑时间 | 时间序列 CSV |
| 人工测点整理 | 日志、现场坐标与测量时间 | 按测点选取代表值 | 二维 Excel / CSV 矩阵 |
| PyQt5 桌面程序 | 二维矩阵 | 原始绘图或二维三次插值 | 可视化及 PNG / JPG / PDF |

实时接收发生在串口记录阶段。桌面程序通过文件导入工作，尚未与串口采集组成实时更新的地图。

## 固件

入口：[wifi_test_LCD.ino](../firmware/wifi_test_LCD/wifi_test_LCD.ino)。

- `setup()` 初始化串口、XL9555 和 LCD，随后连接 Wi-Fi 并等待成功。
- `loop()` 检查连接状态，以 `millis()` 判断采样、刷新和重连间隔。
- `rssiBuffer` 最多保存 5 个样本；每次刷新计算有效样本均值，然后重置计数。
- 掉线时暂停采样，间隔重试连接，并重置缓冲区状态。

尽管代码使用循环索引，平均值输出后会清空计数，实际行为更适合描述为**批次平均**。原程序不是每新增一个样本就更新一次的滑动平均。

## 串口记录器

入口：[wifi强度数据传输加Ave.py](../wifi强度数据传输加Ave.py)。

| 函数 | 职责 |
| --- | --- |
| `setup_serial()` | 以指定端口和波特率打开串口 |
| `init_csv_file()` | 创建或打开日志，仅在文件不存在时写入表头 |
| `parse_line()` | 区分 `RAW` / `AVG`，转换时间和值，并附加电脑时间 |
| `main()` | 循环接收、逐行追加日志，在中断退出时关闭串口 |

端口和文件路径通过脚本顶部常量修改，尚无命令行参数。状态文本会被解析器跳过；串口断开后的自动重新打开尚未实现。

## 桌面可视化

入口：[main.py](../main.py)，GUI 使用 **PyQt5**，Matplotlib 的 Qt 画布嵌入窗口。

| 类 / 方法 | 职责 |
| --- | --- |
| `HeatmapCanvas` | 创建 Matplotlib Figure 并作为 Qt 控件嵌入 |
| `WiFiHeatmapApp` | 组织文件选择、绘图、状态提示与导出按钮 |
| `upload_data()` | 使用 Pandas 读取 Excel 或 CSV，并以首列作为行标签 |
| `show_heatmap(False)` | 使用 `imshow` 绘图，并在单元格中心显示原值 |
| `show_heatmap(True)` | 用矩阵索引构造坐标，插值到 100 × 100 网格后绘图 |
| `save_figure()` | 保存当前 Matplotlib Figure |

### 插值的准确含义

当前代码调用：

```python
grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')
```

对二维输入，SciPy 的 `cubic` 对应分片三次、连续可微的插值曲面，关联 `CloughTocher2DInterpolator`。它与一维三次样条的概念有关，但不应把当前二维实现直接称为一维样条算法。[SciPy 官方说明](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html)

插值提高展示密度，不增加真实测量点。当前实现也没有把墙体几何、传播模型或路由器位置作为算法输入。

### 坐标与色条

- 坐标由 `np.arange()` 生成，表头仅用于刻度标签；非均匀实际间距不会进入插值计算。
- 颜色为红 → 黄 → 绿，弱 → 强；Matplotlib 对每次绘图自动归一化。
- 三次插值可能出现超出原始样本最小值和最大值的估计值。比较两个图时需要查看各自色条，不能只比较颜色。
- 程序没有固定阈值色标、墙体遮罩、楼层平面图或误差评估模块。

## 原始脚本的保留

[温度图.py](../温度图.py) 和 [温度图2.py](../温度图2.py) 是早期独立绘图实现，使用 TkAgg 和写死的 Excel 路径。保留它们用于理解开发过程；日常体验使用 `main.py`。

本次整理保持 Python 核心程序原样。固件仅调整目录、补齐配套文件，并把 Wi-Fi 配置提取为本地头文件，采样和显示逻辑保持原样。
