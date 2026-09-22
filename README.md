# PixelLink

Real-time PC screen mirroring to a TFT display over Wi-Fi.

PixelLink uses a Python Flask server to capture the PC screen and serve each resized frame as RGB565 data. An ESP32 requests the frame over HTTP and displays it on the TFT.

## Main files

- `server.py` — PC screen capture and HTTP frame server
- `PixelLink.ino` — ESP32 TFT receiver
- `firmware/` — additional receiver examples for other boards
- `docs/` — protocol and wiring notes

## Python requirements

Install:

```bash
pip install flask mss pillow
```

Run:

```bash
python server.py
```

The server listens on port `5000` and exposes:

```
http://<PC-IP>:5000/frame
```

## ESP32 setup

Open `PixelLink.ino` in Arduino IDE.

Set your Wi-Fi credentials and the PC IP address in the sketch:

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* server = "http://YOUR_PC_IP:5000/frame";
```

The example uses a `160x128` TFT frame and RGB565 data.

## TFT

The ESP32 example uses TFT_eSPI. Configure TFT_eSPI for your display before uploading.

## Architecture

```
PC / Laptop
   │
   │ server.py
   ▼
Wi-Fi / HTTP
   │
   ▼
ESP32
   │
   │ TFT_eSPI
   ▼
ST7735 TFT
```

## Notes

PixelLink is designed for small TFT displays. The server resizes the captured desktop frame to the TFT resolution before converting it to RGB565.

The main implementation uses HTTP: the ESP32 requests a frame, the Python server returns it, and the ESP32 displays it.

## License

MIT
