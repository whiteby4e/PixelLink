#!/usr/bin/env python3
"""PixelLink PC sender: stream desktop frames to a PixelLink TCP receiver."""

from __future__ import annotations

import argparse
import socket
import struct
import sys
import time

import mss
from PIL import Image

HEADER = struct.Struct("!4sHHII")
MAGIC = b"PLNK"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture the PC screen and stream RGB565 frames to a PixelLink receiver."
    )
    parser.add_argument("--host", required=True, help="IP address of the microcontroller receiver")
    parser.add_argument("--port", type=int, default=5000, help="Receiver TCP port (default: 5000)")
    parser.add_argument("--width", type=int, default=128, help="Frame width (default: 128)")
    parser.add_argument("--height", type=int, default=160, help="Frame height (default: 160)")
    parser.add_argument("--monitor", type=int, default=1, help="MSS monitor index (default: 1)")
    parser.add_argument("--fps", type=float, default=15.0, help="Target frame rate (default: 15)")
    parser.add_argument("--connect-timeout", type=float, default=5.0)
    return parser.parse_args()


def encode_rgb565(image: Image.Image) -> bytes:
    """Encode an RGB image as row-major, big-endian RGB565 bytes."""
    image = image.convert("RGB")
    output = bytearray(image.width * image.height * 2)
    offset = 0

    for red, green, blue in image.getdata():
        value = ((red >> 3) << 11) | ((green >> 2) << 5) | (blue >> 3)
        output[offset] = (value >> 8) & 0xFF
        output[offset + 1] = value & 0xFF
        offset += 2

    return bytes(output)


def capture_frame(capture: mss.mss, monitor: dict, width: int, height: int) -> bytes:
    shot = capture.grab(monitor)
    image = Image.frombytes("RGB", shot.size, shot.rgb)
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    return encode_rgb565(image)


def main() -> int:
    args = parse_args()

    if args.port < 1 or args.port > 65535:
        print("Error: --port must be between 1 and 65535.", file=sys.stderr)
        return 2
    if args.width < 1 or args.width > 65535 or args.height < 1 or args.height > 65535:
        print("Error: width and height must be between 1 and 65535.", file=sys.stderr)
        return 2
    if args.fps <= 0:
        print("Error: --fps must be greater than zero.", file=sys.stderr)
        return 2

    frame_interval = 1.0 / args.fps
    frame_id = 0

    try:
        with mss.mss() as capture:
            if args.monitor < 1 or args.monitor >= len(capture.monitors):
                print(
                    f"Error: monitor {args.monitor} is unavailable. "
                    f"Available monitor indices: 1 to {len(capture.monitors) - 1}.",
                    file=sys.stderr,
                )
                return 2

            monitor = capture.monitors[args.monitor]
            expected_size = args.width * args.height * 2

            print(
                f"PixelLink sender → {args.host}:{args.port} "
                f"({args.width}x{args.height}, {args.fps:g} FPS)"
            )
            print("Press Ctrl+C to stop.")

            while True:
                try:
                    with socket.create_connection(
                        (args.host, args.port), timeout=args.connect_timeout
                    ) as connection:
                        connection.settimeout(None)
                        print("Connected to receiver.")

                        while True:
                            started = time.monotonic()
                            payload = capture_frame(
                                capture, monitor, args.width, args.height
                            )
                            if len(payload) != expected_size:
                                raise RuntimeError("Unexpected RGB565 payload size.")

                            header = HEADER.pack(
                                MAGIC,
                                args.width,
                                args.height,
                                len(payload),
                                frame_id & 0xFFFFFFFF,
                            )
                            connection.sendall(header + payload)
                            frame_id += 1

                            remaining = frame_interval - (time.monotonic() - started)
                            if remaining > 0:
                                time.sleep(remaining)

                except (OSError, TimeoutError) as exc:
                    print(f"Receiver unavailable ({exc}); retrying in 2 seconds.")
                    time.sleep(2)

    except KeyboardInterrupt:
        print("\nPixelLink sender stopped.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
