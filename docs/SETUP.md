# 安装、硬件与采集指南

[返回项目首页](../README.md)

## 先选择使用方式

| 需求 | 所需内容 |
| --- | --- |
| 体验热力图 | Python 环境、[依赖文件](../requirements.txt)、[示例矩阵](../examples/report_grid.csv) |
| 测量自己的房间 | 上述软件，加 DNESP32S3、配套 LCD、USB 数据线和可连接的 2.4 GHz Wi-Fi |

本次软件复核使用 Windows、Python 3.9.5 和 `requirements.txt` 中的版本。该版本记录用于复现既有程序，不代表对所有 Python、操作系统或 Arduino 核心版本完成了兼容性测试。具体检查范围见[验证记录](VALIDATION.md)。

## 安装 Python 依赖

在仓库根目录打开 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
.\.venv\Scripts\python.exe main.py
```

这里直接调用虚拟环境中的 Python，无需调整 PowerShell 的脚本执行策略。`openpyxl` 用于读取 `.xlsx`；`pyserial` 用于串口采集。只体验绘图时，不需要连接开发板。

## 硬件组成

- **主控**：论文中的 DNESP32S3 开发板，搭载 ESP32-S3 / ATK-MWS3S 模块。
- **显示**：配套 2.4 英寸 SPI LCD；代码默认竖屏分辨率为 240 × 320，并设置为横屏显示。
- **I/O 扩展**：XL9555，通过 I²C 控制 LCD 背光和复位。
- **通信**：开发板串口与电脑连接，波特率 115200。
- **网络**：当前固件使用 `WiFi.begin(ssid, password)` 连接指定网络，未配置校园网认证、网页认证或企业级认证流程。

### 代码中的引脚定义

以下表格直接来自随仓库提供的 `spilcd.h` 和 `xl9555.h`。它对应本项目板卡，其他 ESP32-S3 板卡需要自行适配。

| 功能 | 定义 | 引脚 / 地址 |
| --- | --- | --- |
| LCD 片选 | `SLCD_CS_PIN` | GPIO 21 |
| LCD MOSI / 数据 | `SLCD_SDA_PIN` | GPIO 11 |
| LCD SPI 时钟 | `SLCD_SCK_PIN` | GPIO 12 |
| LCD MISO | `SLCD_SDI_PIN` | `-1`，未使用 |
| LCD 命令 / 数据选择 | `SLCD_WR_PIN` | GPIO 40 |
| XL9555 I²C 时钟 | `IIC_SCL` | GPIO 42 |
| XL9555 I²C 数据 | `IIC_SDA` | GPIO 41 |
| XL9555 中断 | `IIC_INT_PIN` | GPIO 0；原注释说明需跳线帽连接 |
| XL9555 设备地址 | `EXIO_ADDR` | `0x20`（7 位） |
| LCD 背光 | `SLCD_PWR` | XL9555 P13 |
| LCD 复位 | `SLCD_RST` | XL9555 P12 |

LCD 模块使用 3.3 V 电源并共地。使用配套接口时，按板卡手册连接；不要把 XL9555 的 P12/P13 当成 ESP32 GPIO 12/13。

## 准备与上传固件

1. 在 Arduino IDE 中安装 Espressif 的 ESP32 开发板支持包，并选择与实际开发板相符的 ESP32-S3 配置和串口。
2. 参考 [Espressif 官方安装文档](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)。中国大陆网络可优先使用文档中的 [Jihulab 稳定版索引](https://jihulab.com/esp-mirror/espressif/arduino-esp32/-/raw/gh-pages/package_esp32_index_cn.json)。原工程未记录完整的 Arduino IDE 与板卡菜单配置，本次整理未新增“已验证”的硬件版本声明。
3. 复制 Wi-Fi 配置模板：

   ```powershell
   Copy-Item firmware/wifi_test_LCD/wifi_config.example.h firmware/wifi_test_LCD/wifi_config.h
   ```

4. 编辑生成的 `wifi_config.h`，填写 `WIFI_SSID` 和 `WIFI_PASSWORD`。该文件已被 Git 忽略。
5. 打开 [firmware/wifi_test_LCD/wifi_test_LCD.ino](../firmware/wifi_test_LCD/wifi_test_LCD.ino)。保持 `.ino`、驱动和字库位于同一文件夹，文件夹名应为 `wifi_test_LCD`。
6. 编译并上传到开发板，打开 115200 波特率串口监视器核对输出。连接成功后，LCD 应周期性显示 `Avg: ... dBm`。

`spilcd.cpp` 中 `SPI_LCD_TYPE` 默认是 `1`，对应 2.4 英寸屏。Wi-Fi、SPI 和 Wire 使用 Arduino-ESP32 提供的库；该草图没有使用 TFT_eSPI。

### 采样行为

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| `SAMPLE_INTERVAL` | 1000 ms | RSSI 采样间隔 |
| `BUFFER_SIZE` | 5 | 最多缓存 5 个读数 |
| `REFRESH_INTERVAL` | 5000 ms | 平均值计算与 LCD 刷新间隔 |
| `RECONNECT_INTERVAL` | 3000 ms | 采集循环中断线后的重试间隔 |

每次输出平均值后会清空当前计数，因此是分批平均。启动或恢复连接后的批次可能不足 5 个有效样本，时间间隔也受循环执行影响。

**首次连接的行为**：`setup()` 会一直等待 Wi-Fi 连接，尚未实现连接超时；约 3 秒一次的重连逻辑位于后续 `loop()` 中。

## 记录串口数据

1. 在设备管理器中确认实际 COM 端口。
2. 编辑 [wifi强度数据传输加Ave.py](../wifi强度数据传输加Ave.py) 顶部的 `SERIAL_PORT`，默认是 `COM4`；必要时调整 `CSV_FILE`。
3. 关闭 Arduino 串口监视器，释放串口。
4. 在仓库根目录执行：

   ```powershell
   .\.venv\Scripts\python.exe "wifi强度数据传输加Ave.py"
   ```

5. 按 `Ctrl+C` 停止采集。默认结果保存为运行目录下的 `wifi_data_analysis.csv`；同名文件会追加记录，不会自动创建独立实验文件。

预期数据行如下，数值仅用于解释协议：

```text
RAW,1000,-42
RAW,2000,-41
AVG,5000,-41.6
```

脚本没有自动定位功能。每个测点需要额外记录坐标、停留时段和选用的平均值；移动过程中产生的读数不应直接归给到达后的测点。整理方法见[数据格式说明](DATA_FORMAT.md)。

## 常见问题

| 现象 | 检查方法 |
| --- | --- |
| `No module named PyQt5` 等导入错误 | 使用安装依赖的同一个 `.venv` Python 启动程序 |
| `.xlsx` 无法打开 | 确认已安装 `openpyxl`；只保留一个规则的数值矩阵，首列作行标签 |
| 缺少 `wifi_config.h` | 复制同目录中的 `wifi_config.example.h`，再填写网络信息 |
| 缺少 `spilcd.h` / `xl9555.h` | 从 `firmware/wifi_test_LCD/` 打开完整草图，不要单独复制 `.ino` |
| LCD 一直显示连接提示 | 检查 SSID、密码、2.4 GHz 频段和网络认证方式；首次连接没有超时退出 |
| 串口无法打开 | 检查 COM 端口、USB 数据线，以及串口是否被 Arduino 或其他工具占用 |
| 日志出现“unknown data type” | 连接和重连提示不是 `RAW` / `AVG` 数据行，原脚本会报提示并跳过 |
| 插值失败或显示空白 | 排除空值、文字、混合格式和单行 / 单列矩阵，先使用仓库示例验证环境 |
| 图像强弱方向与房间不符 | 第一条数据行显示在顶部；按实际空间关系整理 y 标签和行顺序 |
| 两张图颜色看起来不同 | 程序对每张图单独归一化，比较时应同时查看色条的数值范围 |
| 早期脚本找不到 Excel | `温度图.py`、`温度图2.py` 中包含旧电脑绝对路径；推荐使用 `main.py` 文件选择界面 |

程序当前缺少完整的数据校验和异常恢复，请先用示例矩阵确认环境，再导入自己的测量数据。
