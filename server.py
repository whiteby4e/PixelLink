import os
import threading
import time

import mss
from flask import Flask, Response
from PIL import Image

app = Flask(__name__)

WIDTH = int(os.getenv("PIXELLINK_WIDTH", "160"))
HEIGHT = int(os.getenv("PIXELLINK_HEIGHT", "128"))
MONITOR_INDEX = max(1, int(os.getenv("PIXELLINK_MONITOR", "1")))
MAX_FPS = max(1, int(os.getenv("PIXELLINK_MAX_FPS", "15")))

sct = mss.mss()
frame_lock = threading.Lock()
cached_frame = None
cached_at = 0.0


def capture_frame():
    global cached_frame, cached_at

    now = time.monotonic()
    with frame_lock:
        if cached_frame is not None and now - cached_at < 1.0 / MAX_FPS:
            return cached_frame

        monitors = sct.monitors
        index = MONITOR_INDEX if MONITOR_INDEX < len(monitors) else 1
        shot = sct.grab(monitors[index])
        image = Image.frombytes("RGB", shot.size, shot.rgb)
        image = image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

        pixels = image.load()
        rgb565 = bytearray(WIDTH * HEIGHT * 2)
        pos = 0
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b = pixels[x, y]
                value = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                rgb565[pos] = value >> 8
                rgb565[pos + 1] = value & 0xFF
                pos += 2

        cached_frame = bytes(rgb565)
        cached_at = now
        return cached_frame


@app.route("/frame")
def frame():
    data = capture_frame()
    response = Response(data, mimetype="application/octet-stream")
    response.headers["X-PixelLink-Width"] = str(WIDTH)
    response.headers["X-PixelLink-Height"] = str(HEIGHT)
    response.headers["X-PixelLink-Pixel-Format"] = "RGB565-BE"
    return response


@app.route("/health")
def health():
    return {
        "status": "ok",
        "width": WIDTH,
        "height": HEIGHT,
        "max_fps": MAX_FPS,
        "monitor": MONITOR_INDEX,
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
