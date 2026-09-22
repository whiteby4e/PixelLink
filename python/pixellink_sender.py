"""PixelLink PC screen capture and TCP streaming client."""

from __future__ import annotations

import argparse
import socket
import struct
import time

import mss
import numpy as np
from PIL import Image

MAGIC = b"PLNK"
HEADER = struct.Struct("!4sHHII")
DEFAULT_WIDTH = 128
DEFAULT_HEIGHT = 160
DEFAULT_FPS = 20


def frame_to_rgb565(frame: np.ndarray, width: int, height: int) -> bytes:
    """Resize a BGRA screen frame and convert it to RGB565 bytes."""
    rgb = frame[:, :, :3][:, :, ::-1]
    image = Image.fromarray(rgb, "RGB").resize((width, height), Image.Resampling.BILINEAR)
    pixels = np.asarray(image, dtype=np.uint16)

    red = pixels[:, :, 0] >> 3
    green = pixels[:, :, 1] >> 2
    blue = pixels[:, :, 2] >> 3
    rgb565 = (red << 11) | (green << 5) | blue

    return rgb565.astype(">u2", copy=False).tobytes()


def stream(host: str, port: int, width: int, height: int, fps: int) -> None:
    """Capture the primary monitor and stream frames to one receiver."""
    interval = 1.0 / fps
    frame_id = 0

    with mss.mss() as capture:
        monitor = capture.monitors[1]

        with socket.create_connection((host, port), timeout=5) as sock:
            sock.settimeout(None)
            print(f"Connected to {host}:{port}")
            print(f"Streaming {width}x{height} at up to {fps} FPS")

            while True:
                started = time.perf_counter()
                frame = np.asarray(capture.grab(monitor))
                payload = frame_to_rgb565(frame, width, height)

                header = HEADER.pack(
                    MAGIC,
                    width,
                    height,
                    len(payload),
                    frame_id,
                )
                sock.sendall(header)
                sock.sendall(payload)

                frame_id = (frame_id + 1) & 0xFFFFFFFF
                elapsed = time.perf_counter() - started
                time.sleep(max(0.0, interval - elapsed))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stream a PC screen to PixelLink.")
    parser.add_argument("--host", required=True, help="Receiver IP address.")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not 1 <= args.width <= 320 or not 1 <= args.height <= 320:
        raise SystemExit("Width and height must be between 1 and 320.")
    if not 1 <= args.fps <= 60:
        raise SystemExit("FPS must be between 1 and 60.")

    while True:
        try:
            stream(args.host, args.port, args.width, args.height, args.fps)
        except (ConnectionError, OSError) as exc:
            print(f"Connection lost: {exc}")
            print("Retrying in 2 seconds...")
            time.sleep(2)


if __name__ == "__main__":
    main()
