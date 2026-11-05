#include <WiFi.h>
#include "spilcd.h"
#include "xl9555.h"
#include "wifi_config.h"

// 复制 wifi_config.example.h 为 wifi_config.h，并填写自己的 WiFi 配置。
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

// LCD配置
#define REFRESH_INTERVAL 5000  // 5秒刷新间隔
#define FONT_SIZE LCD_FONT_24
#define TEXT_COLOR BLACK
#define BG_COLOR WHITE
#define WARNING_COLOR RED     // 新增警告颜色

// 数据统计配置
#define SAMPLE_INTERVAL 1000    // 采样间隔1秒
#define BUFFER_SIZE 5           // 5秒数据缓冲区
#define RECONNECT_INTERVAL 3000 // 重连间隔3秒

// 全局变量
int32_t rssiBuffer[BUFFER_SIZE];
uint8_t dataIndex = 0;
bool bufferFull = false;
uint32_t lastReconnectAttempt = 0;  // 最后重连时间戳

void setup() {
  Serial.begin(115200);
  
  // 初始化LCD
  xl9555_init();
  lcd_init();
  lcd_display_dir(1);
  lcd_clear(BG_COLOR);
  
  // 显示连接提示
  lcd_show_string(20, 50, 240, 30, FONT_SIZE, "Connecting WiFi...", TEXT_COLOR);
  
  // 连接WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    lcd_show_string(20, 80, 240, 30, FONT_SIZE, ".", TEXT_COLOR);
  }
  
  lcd_fill(20, 50, 240, 100, BG_COLOR);
}

void loop() {
  static uint32_t lastSampleTime = 0;
  static uint32_t lastRefreshTime = 0;

  // Continuous monitoring of WiFi status
  if (WiFi.status() != WL_CONNECTED) {
    // WiFi Disconnection Processing
    //lcd_fill(20, 50, 240, 80, BG_COLOR);  // Clear original display
    lcd_show_string(20, 50, 240, 30, FONT_SIZE, "WiFi Disconnected!", WARNING_COLOR);
    Serial.println("WiFi Disconnected!");
    
    // Reconnection attempts with intervals
    if (millis() - lastReconnectAttempt >= RECONNECT_INTERVAL) {
      lastReconnectAttempt = millis();
      WiFi.reconnect();
      Serial.println("Attempting to reconnect...");
      
      // Reset Data Buffer
      dataIndex = 0;
      bufferFull = false;
    }
    return;  // Skip subsequent processing when disconnected
  }

  // Sampling data (performed only in the connected state)
  if (millis() - lastSampleTime >= SAMPLE_INTERVAL) {
    lastSampleTime = millis();
    
    // Storing data into a buffer
    rssiBuffer[dataIndex] = WiFi.RSSI();
    dataIndex++;
    
    if (dataIndex >= BUFFER_SIZE) {
      dataIndex = 0;
      bufferFull = true;
    }
    
    Serial.print("RAW,");
    Serial.print(millis());
    Serial.print(",");
    Serial.println(rssiBuffer[dataIndex ? dataIndex-1 : BUFFER_SIZE-1]);
  }

  // Calculates and displays the average value every 5 seconds
  if (millis() - lastRefreshTime >= REFRESH_INTERVAL) {
    lastRefreshTime = millis();
    
    if (bufferFull || dataIndex > 0) {
      int validSamples = bufferFull ? BUFFER_SIZE : dataIndex;
      int32_t sum = 0;
      
      for(int i=0; i<validSamples; i++){
        sum += rssiBuffer[i];
      }
      float average = (float)sum / validSamples;

      // LCD显示
      char displayStr[32];
      snprintf(displayStr, sizeof(displayStr), "Avg: %.1f dBm", average);
      lcd_fill(20, 50, 240, 80, BG_COLOR);
      lcd_show_string(20, 50, 240, 30, FONT_SIZE, displayStr, TEXT_COLOR);

      // 串口输出
      Serial.print("AVG,");
      Serial.print(millis());
      Serial.print(",");
      Serial.println(average, 1);
      
      // 重置缓冲区
      dataIndex = 0;
      bufferFull = false;
    }
  }
}
