# 内容来源与整理说明

[返回项目首页](../README.md)

## 论文

- **作者**：石然冰（Shi Ranbing）
- **题目**：室内 WiFi 信号强度映射系统的设计与研究 / Design and Research of an Indoor WiFi Signal Strength Mapping System
- **学校与专业**：北京交通大学兰卡斯特大学学院，电子与通信工程
- **封面日期**：2025 年 5 月 3 日
- **整理依据**：作者提供的 `21721065 Shi Ranbing Final Report.pdf`，共 47 个 PDF 页面。

仓库收录项目说明和相关图像。论文全文、签名页及其他个人材料未作为仓库文件发布。

## 图像与数据出处

图片直接从 PDF 的嵌入图像中提取，未重新绘制或改变实验数值。PDF 页码按文件第一页为 1 计数，“正文页码”按论文页面印刷的数字计数。

| 仓库文件 | 论文图号 | PDF 页码 | 正文页码 | 内容 |
| --- | --- | --- | --- | --- |
| [hardware.jpg](assets/hardware.jpg) | 图 7 | 15 | 9 | 硬件连接实物 |
| [lcd-reading.jpg](assets/lcd-reading.jpg) | 图 13 | 19 | 13 | 平均 RSSI 本地显示 |
| [measurement-table.png](assets/measurement-table.png) | 图 20 | 22 | 16 | 测点矩阵 |
| [heatmap-raw.png](assets/heatmap-raw.png) | 图 30 | 30 | 24 | 原始热力图 |
| [heatmap-interpolated.png](assets/heatmap-interpolated.png) | 图 31 | 31 | 25 | 插值热力图 |
| [desktop-ui.png](assets/desktop-ui.png) | 图 33 | 34 | 28 | 桌面程序界面 |
| [report_grid.csv](../examples/report_grid.csv) | 图 20、图 30 | 22、30 | 16、24 | 人工转录并交叉核对的 30 个值 |

`report_grid.csv` 是展示矩阵转录件，不是恢复出的原始 Excel 文件或完整实验日志。

## 源码来源

- `main.py`、`wifi强度数据传输加Ave.py`、`温度图.py`、`温度图2.py` 沿用仓库原始版本；本地 `WiFiHeatmap/main.py` 与仓库版本一致。
- `wifi_test_LCD.ino` 从仓库根目录移入 `firmware/wifi_test_LCD/`，并将原有网络配置改为读取 `wifi_config.h`。
- `spilcd.cpp`、`spilcd.h`、`xl9555.cpp`、`xl9555.h` 和 `font.h` 来自作者保留的 `code/wifi_test_LCD/`，原样补入。它们属于板卡配套驱动及字库，保留了现有文件注释；本次整理不将其声明为新编写的算法或重新授权。
- 开发工具安装包、ESP-IDF 整套环境、可执行文件和压缩包不属于源码复现所必需的仓库内容。

### 板卡驱动署名

本地板卡资料 `11_spi_lcd/spilcd.cpp` 的原始文件头标明作者为 **正点原子团队（ALIENTEK）**，版本 V1.0，日期 2023-12-01，并保留以下版权声明：

```text
Copyright (c) 2020-2032, 广州市星翼电子科技有限公司
```

本项目工作目录中的对应驱动使用了简化文件头，本次补齐保持其原样，并在此补充可核查的上游署名。该署名是来源记录，不构成新的许可授权。

本仓库尚无统一开源许可证。作者代码、论文图片与板卡配套文件的来源应分别保留，不能因补齐文件就推断其适用同一许可证。

## 以实际实现为准的表述

| 论文中出现的表述 | 本仓库的说明 |
| --- | --- |
| 部分章节提到 Web 或 Tkinter 界面 | `main.py` 实际使用 PyQt5；早期独立绘图脚本使用 TkAgg |
| 串口数据保存为 Excel / CSV | 现有采集脚本写入 CSV；绘图程序支持 Excel 与 CSV |
| 5 秒滑动窗口 | 固件每批平均后清空计数，更准确地描述为批次平均 |
| 重连处理 | 周期重连在 `loop()` 中；`setup()` 首次连接会持续等待 |
| 三次样条 / 插值提高精度 | 二维 `griddata(method='cubic')` 用于连续展示；未给出独立误差验证 |
| 实时系统 | 串口采集可连续进行；空间矩阵整理和地图生成仍为离线流程 |

## 外部技术参考

- [SciPy：griddata 的二维 cubic 语义](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html)
- [Espressif：Arduino-ESP32 安装与中国大陆镜像](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)

技术参考用于核对实现说明与安装路径，不作为本项目实验结果的证据。
