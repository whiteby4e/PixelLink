# PixelLink

Real-time screen mirroring from a PC to a microcontroller-driven TFT display over Wi-Fi using Python.

PixelLink captures the PC screen, scales it to the TFT resolution, converts each frame to RGB565, and streams the frames over TCP. The receiver draws each frame directly to the TFT.

## Architecture

```
PC / Laptop
   │
   │ Python + mss + Pillow + NumPy
   ▼
Wi-Fi / TCP
   │
   ▼
ESP32 / ESP8266 / Arduino WiFiNINA / Pico W
   │
   ▼
SPI TFT display
```

## Repository layout

- `python/` — PC screen capture and streaming client
- `firmware/esp32/` — ESP32 receiver
- `firmware/esp8266/` — ESP8266 receiver
- `firmware/arduino_wifi_nina/` — Arduino boards using WiFiNINA
- `firmware/pico_w/` — Raspberry Pi Pico W receiver
- `docs/` — protocol and wiring notes

## Python requirements

Install:

```bash
pip install -r python/requirements.txt
```

Run:

```bash
python python/pixellink_sender.py --host 192.168.1.50
```

The default stream resolution is 128×160. Change it with `--width` and `--height`.

## Receiver setup

Each firmware example uses the same PixelLink TCP frame protocol. Set the Wi-Fi SSID/password and the PC IP address where required, then upload the matching example for your board.

The display code uses Adafruit GFX/ST7735, so the same TFT wiring can be adapted to several supported boards.

## Notes

PixelLink is designed for small TFT displays rather than full desktop-resolution video. The stream is resized before transmission to keep bandwidth and memory usage reasonable.

The current protocol sends RGB565 frame data without JPEG decoding on the microcontroller. This keeps the receiver simple and avoids requiring a JPEG decoder library.

## License

MIT
