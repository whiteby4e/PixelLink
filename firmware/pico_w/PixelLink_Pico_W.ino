#include <WiFi.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

constexpr uint16_t TFT_WIDTH = 128;
constexpr uint16_t TFT_HEIGHT = 160;
constexpr uint16_t SERVER_PORT = 5000;

#define TFT_CS 17
#define TFT_DC 20
#define TFT_RST 21

Adafruit_ST7735 tft(TFT_CS, TFT_DC, TFT_RST);
WiFiServer server(SERVER_PORT);

uint8_t header[16];
uint8_t frameBuffer[TFT_WIDTH * TFT_HEIGHT * 2];

bool readExact(WiFiClient& client, uint8_t* buffer, size_t length) {
  size_t received = 0;
  while (received < length) {
    int count = client.read(buffer + received, length - received);
    if (count <= 0) return false;
    received += static_cast<size_t>(count);
  }
  return true;
}

bool readFrame(WiFiClient& client) {
  if (!readExact(client, header, sizeof(header))) return false;
  if (memcmp(header, "PLNK", 4) != 0) return false;

  uint16_t width = (static_cast<uint16_t>(header[4]) << 8) | header[5];
  uint16_t height = (static_cast<uint16_t>(header[6]) << 8) | header[7];
  uint32_t payloadLength =
      (static_cast<uint32_t>(header[8]) << 24) |
      (static_cast<uint32_t>(header[9]) << 16) |
      (static_cast<uint32_t>(header[10]) << 8) |
      header[11];

  if (width != TFT_WIDTH || height != TFT_HEIGHT) return false;
  if (payloadLength != sizeof(frameBuffer)) return false;
  if (!readExact(client, frameBuffer, payloadLength)) return false;

  tft.startWrite();
  tft.setAddrWindow(0, 0, TFT_WIDTH, TFT_HEIGHT);
  for (size_t i = 0; i < sizeof(frameBuffer); i += 2) {
    uint16_t color = (static_cast<uint16_t>(frameBuffer[i]) << 8) | frameBuffer[i + 1];
    tft.pushColor(color);
  }
  tft.endWrite();
  return true;
}

void setup() {
  Serial.begin(115200);
  tft.initR(INITR_BLACKTAB);
  tft.setRotation(0);
  tft.fillScreen(ST77XX_BLACK);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) delay(250);

  Serial.print("Receiver IP: ");
  Serial.println(WiFi.localIP());
  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (!client) return;

  while (client.connected()) {
    if (!readFrame(client)) break;
  }
  client.stop();
}
