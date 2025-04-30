import serial
import csv
from datetime import datetime
import time
import sys
import os

# 配置参数
SERIAL_PORT = 'COM4'  # 串口号
BAUDRATE = 115200  # 波特率
CSV_FILE = 'wifi_data_analysis.csv'  # 文件名

# CSV文件列定义
CSV_COLUMNS = [
    "PC Time",
    "Data Type",  # RAW/AVG
    "ESP32 Timestamp (ms)",
    "RSSI (dBm)",  # 原始值
    "Average (dBm)"  # 平均值
]


def setup_serial():
    """Initialising the serial port connection"""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"✅ Successfully connected to the serial port {SERIAL_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"❌ Serial port connection failure: {str(e)}")
        print("Possible causes：")
        print("1. The serial port is occupied by another program")
        print("2. Device not properly connected")
        sys.exit(1)


def init_csv_file():
    """初始化CSV文件"""
    file_exists = os.path.exists(CSV_FILE)

    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(CSV_COLUMNS)
                print("📄 已创建新CSV文件并写入表头")
    except Exception as e:
        print(f"❌ 文件初始化失败: {str(e)}")
        sys.exit(1)


def parse_line(line):
    """Parsing data rows"""
    try:
        parts = line.strip().split(',')
        data_type = parts[0]

        if data_type not in ('RAW', 'AVG'):
            raise ValueError("unknown data type")

        esp_time = int(parts[1])
        value = float(parts[2]) if data_type == 'AVG' else int(parts[2])
        pc_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        return {
            "pc_time": pc_time,
            "data_type": data_type,
            "esp_time": esp_time,
            "rssi": value if data_type == 'RAW' else None,
            "average": value if data_type == 'AVG' else None
        }
    except Exception as e:
        print(f"⚠️ Data parsing failure: {line} | error: {str(e)}")
        return None


def main():
    init_csv_file()
    ser = setup_serial()

    print("\n🔍 开始监听数据...（按 Ctrl+C 停止）")
    try:
        while True:
            if ser.in_waiting > 0:
                raw_line = ser.readline()
                try:
                    line = raw_line.decode('utf-8').strip()
                except UnicodeDecodeError:
                    print(f"⚠️ 解码失败，原始数据: {raw_line}")
                    continue

                if not line:
                    continue

                # 解析数据
                data = parse_line(line)
                if not data:
                    continue

                # Write to CSV
                with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    row = [
                        data['pc_time'],
                        data['data_type'],
                        data['esp_time'],
                        data['rssi'] if data['data_type'] == 'RAW' else '',
                        data['average'] if data['data_type'] == 'AVG' else ''
                    ]
                    writer.writerow(row)

                # 终端显示
                if data['data_type'] == 'RAW':
                    print(f"[{data['pc_time']}] RAW: {data['rssi']}dBm")
                else:
                    print(f"[{data['pc_time']}] 🚀 AVG: {data['average']:.1f}dBm")

    except KeyboardInterrupt:
        print("\n🛑 用户中断，停止监听...")
    finally:
        ser.close()
        print(f"💾 数据已保存至: {os.path.abspath(CSV_FILE)}")


if __name__ == "__main__":
    main()