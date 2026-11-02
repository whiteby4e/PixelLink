<div align="center">

# PixelLink

**Mirror your PC screen onto a small TFT over Wi-Fi.**

PixelLink captures desktop frames, converts them to RGB565, and streams them to a microcontroller receiver for display on a TFT.

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
Wi-Fi / TCP (PLNK frames)
    │
    ▼
Microcontroller receiver
    │
    ▼
ST7735 TFT display
```

The PC sender opens a TCP connection to the microcontroller. Each frame contains a 16-byte `PLNK` header followed by RGB565 pixel data.

## ✨ Features

- Capture the PC desktop with MSS.
- Resize frames for a small TFT display.
- Convert RGB888 pixels to big-endian RGB565.
- Stream frames over TCP with automatic reconnect.
- Configure target resolution, monitor, and frame rate.
- Includes receiver examples for ESP32, ESP8266, Pico W, and Arduino WiFiNINA.

## ⚡ Quick start

### 1. Install dependencies

```bash
git clone https://github.com/whiteby4e/PixelLink.git
cd PixelLink
python -m pip install -r python/requirements.txt
```

### 2. Upload receiver firmware

Choose the example for your board:

| Board family | Firmware |
|---|---|
| ESP32 | [ESP32 receiver](firmware/esp32/PixelLink_ESP32.ino) |
| ESP8266 | [ESP8266 receiver](firmware/esp8266/PixelLink_ESP8266.ino) |
| Raspberry Pi Pico W | [Pico W receiver](firmware/pico_w/PixelLink_Pico_W.ino) |
| Arduino WiFiNINA | [WiFiNINA receiver](firmware/arduino_wifi_nina/PixelLink_Arduino_WiFiNINA.ino) |

Set the Wi-Fi name and password in the sketch, configure the ST7735 pins, and upload it. Open the Serial Monitor at 115200 baud to find the receiver's IP address.

### 3. Start the PC sender

Replace the example address with the IP printed by your receiver:

```bash
python sender.py --host 192.168.1.50
```

The sender defaults to 128 × 160 at 15 FPS and TCP port 5000. Keep the PC and receiver on the same local network.

To change the monitor or frame rate:

```bash
python sender.py --host 192.168.1.50 --monitor 1 --fps 10
```

Press **Ctrl+C** to stop.

## ⚙️ Sender options

| Option | Default | Purpose |
|---|---:|---|
| `--host` | Required | Receiver IP address |
| `--port` | `5000` | Receiver TCP port |
| `--width` | `128` | Frame width |
| `--height` | `160` | Frame height |
| `--monitor` | `1` | MSS monitor index |
| `--fps` | `15` | Target frame rate |

The dimensions must match the receiver firmware's configured TFT dimensions.

## 📡 Frame protocol

The TCP receiver expects a 16-byte network-order header:

| Offset | Size | Field |
|---:|---:|---|
| 0 | 4 | Magic bytes: `PLNK` |
| 4 | 2 | Width |
| 6 | 2 | Height |
| 8 | 4 | Payload length |
| 12 | 4 | Frame ID |

The payload contains exactly `width × height × 2` bytes of row-major RGB565 data, most-significant byte first. The sender uses `sendall()`; the receiver reads the complete header and payload because TCP may split data across packets.

See [protocol notes](docs/PROTOCOL.md) and [TFT wiring](docs/WIRING.md).

## 🧰 Optional HTTP preview endpoint

The repository also contains `server.py`, a small Flask endpoint that exposes a captured RGB565 frame at `/frame` and status at `/health`. This is a separate HTTP utility; it is **not** the TCP sender used by the included receiver firmware.

Run it with:

```bash
python server.py
```

It listens on port 5000 on the PC. If you use it, remember that it is a development endpoint without authentication or encryption.

## 🔐 Network note

The receiver and optional HTTP endpoint are intended for trusted local networks. Neither provides transport encryption or authentication. Do not expose them directly to the public internet.

## 📁 Project layout

```text
PixelLink/
├── sender.py
├── server.py
├── PixelLink.ino
├── firmware/
├── docs/
└── python/requirements.txt
```

## 📄 License

MIT — see [LICENSE](LICENSE).
