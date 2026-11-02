<div align="center">

# PixelLink

**Mirror your PC screen onto a small TFT over Wi-Fi.**

PixelLink captures a desktop frame on a computer, converts it to RGB565, and sends it to a microcontroller that displays it on a TFT screen.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%7C%20ESP8266%20%7C%20Pico%20W-blue)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 🖥️ How it works

```text
PC / Laptop
    │
    ▼
Python screen capture
    │
    ▼
Resize + RGB565 conversion
    │
    ▼
Wi-Fi network
    │
    ▼
Microcontroller receiver
    │
    ▼
ST7735 TFT display
```

The main PC implementation uses Flask, MSS, and Pillow. The repository also contains receiver examples for several Wi-Fi-capable boards.

## ✨ Features

- Capture the desktop on a PC.
- Resize frames for a small TFT display.
- Convert RGB888 pixels to RGB565.
- Serve frames over HTTP.
- Configure frame dimensions, monitor selection, and maximum capture rate with environment variables.
- Includes firmware examples for ESP32, ESP8266, Pico W, and Arduino WiFiNINA.

## ⚡ Quick start: PC server

### 1. Install dependencies

```bash
git clone https://github.com/whiteby4e/PixelLink.git
cd PixelLink
python -m pip install -r python/requirements.txt
```

### 2. Start the server

```bash
python server.py
```

The server listens on port **5000** and provides:

- `/frame` — raw RGB565 frame data.
- `/health` — basic server status and frame configuration.

The frame endpoint returns width, height, and pixel-format metadata in HTTP response headers.

### 3. Configure the receiver

Open the firmware example for your board and set the Wi-Fi network name, password, and PC server address as required by that sketch.

Make sure the PC and microcontroller are connected to the same local network and that the PC firewall allows the connection.

## 📟 Supported receiver examples

| Board family | Firmware |
|---|---|
| ESP32 | [ESP32 receiver](firmware/esp32/PixelLink_ESP32.ino) |
| ESP8266 | [ESP8266 receiver](firmware/esp8266/PixelLink_ESP8266.ino) |
| Raspberry Pi Pico W | [Pico W receiver](firmware/pico_w/PixelLink_Pico_W.ino) |
| Arduino WiFiNINA | [WiFiNINA receiver](firmware/arduino_wifi_nina/PixelLink_Arduino_WiFiNINA.ino) |

The examples use an ST7735 128 × 160 display. Check [wiring notes](docs/WIRING.md) and configure the display library for your board.

## ⚙️ Server configuration

The Python server reads these environment variables:

| Variable | Default | Purpose |
|---|---:|---|
| `PIXELLINK_WIDTH` | `160` | Output frame width |
| `PIXELLINK_HEIGHT` | `128` | Output frame height |
| `PIXELLINK_MONITOR` | `1` | Monitor index |
| `PIXELLINK_MAX_FPS` | `15` | Maximum capture rate |

Set these before launching `server.py` if you need a different frame size or capture rate.

## 📡 Protocol and wiring

- [TFT wiring guide](docs/WIRING.md)
- [Frame protocol notes](docs/PROTOCOL.md)

The HTTP `/frame` endpoint serves raw RGB565 bytes. The protocol document describes a separate 16-byte TCP frame header; do not assume that header is present in the current HTTP response.

## 🔐 Network note

The development server binds to `0.0.0.0` so devices on the local network can connect. It does not provide authentication or encryption. Use it only on a trusted network and do not expose the port directly to the public internet.

## 📁 Project layout

```text
PixelLink/
├── server.py
├── PixelLink.ino
├── firmware/
├── docs/
└── python/requirements.txt
```

## 📄 License

MIT — see [LICENSE](LICENSE).
