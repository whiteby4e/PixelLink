#include <WiFi.h>
#include <HTTPClient.h>
#include <TFT_eSPI.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* server = "http://YOUR_PC_IP:5000/frame";

#define TFT_W 160
#define TFT_H 128
#define FRAME_SIZE (TFT_W * TFT_H * 2)

TFT_eSPI tft = TFT_eSPI();
uint16_t frameBuffer[TFT_W * TFT_H];

void showMessage(const char *msg, uint16_t color = TFT_WHITE)
{
  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(color);
  tft.setCursor(0, 0);
  tft.println(msg);
}

void setup()
{
  Serial.begin(115200);

  tft.init();
  tft.setRotation(1);
  tft.setSwapBytes(false);

  showMessage("Connecting WiFi...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(500);
  }

  Serial.println();
  Serial.println(WiFi.localIP());

  showMessage("WiFi OK", TFT_GREEN);
  delay(1000);
}

void loop()
{
  if (WiFi.status() != WL_CONNECTED)
  {
    showMessage("Reconnect...", TFT_YELLOW);
    WiFi.disconnect();
    WiFi.begin(ssid, password);
    delay(1000);
    return;
  }

  HTTPClient http;
  http.setTimeout(3000);

  if (!http.begin(server))
  {
    showMessage("HTTP Begin Err", TFT_RED);
    delay(1000);
    return;
  }

  int code = http.GET();

  Serial.print("HTTP=");
  Serial.println(code);

  if (code != HTTP_CODE_OK)
  {
    showMessage("HTTP ERROR", TFT_RED);
    http.end();
    delay(500);
    return;
  }

  int len = http.getSize();

  if (len != FRAME_SIZE)
  {
    showMessage("Wrong Size", TFT_RED);
    http.end();
    delay(500);
    return;
  }

  WiFiClient* stream = http.getStreamPtr();
  uint8_t* ptr = reinterpret_cast<uint8_t*>(frameBuffer);
  int received = 0;
  unsigned long start = millis();

  while (received < FRAME_SIZE)
  {
    if (millis() - start > 3000)
    {
      Serial.println("Timeout");
      break;
    }

    int available = stream->available();

    if (available)
    {
      int toRead = min(available, FRAME_SIZE - received);
      int count = stream->read(ptr + received, toRead);

      if (count > 0)
        received += count;
    }

    delay(1);
  }

  http.end();

  if (received != FRAME_SIZE)
  {
    Serial.print("Received=");
    Serial.println(received);
    showMessage("Frame Error", TFT_RED);
    delay(300);
    return;
  }

  tft.pushImage(0, 0, TFT_W, TFT_H, frameBuffer);
}
