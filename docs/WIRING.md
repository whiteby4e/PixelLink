# TFT Wiring

The exact pins depend on the board and TFT module. The examples use SPI and assume a 128×160 ST7735 display.

## ESP32

The example defaults to:

- CS: GPIO 5
- DC: GPIO 2
- RST: GPIO 4
- MOSI/SCK: hardware SPI pins

## ESP8266

The example defaults to:

- CS: D2
- DC: D1
- RST: D0
- MOSI/SCK: hardware SPI pins

## Arduino WiFiNINA

The example defaults to:

- CS: D10
- DC: D9
- RST: D8
- MOSI/SCK: hardware SPI pins

## Pico W

The example uses:

- CS: GP17
- DC: GP20
- RST: GP21
- MOSI/SCK: hardware SPI pins selected by the board core

Adjust the pins to match your physical wiring. Check the TFT module's voltage and logic-level requirements before connecting power or signals.
