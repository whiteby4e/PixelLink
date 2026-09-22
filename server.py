from flask import Flask, Response
from PIL import Image
import mss

app = Flask(__name__)

WIDTH = 160
HEIGHT = 128

sct = mss.mss()

@app.route("/frame")
def frame():

    monitor = sct.monitors[1]

    shot = sct.grab(monitor)

    img = Image.frombytes("RGB", shot.size, shot.rgb)

    img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    pixels = img.load()

    rgb565 = bytearray()

    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = pixels[x, y]

            color = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)

            rgb565.append(color >> 8)
            rgb565.append(color & 0xFF)

    return Response(
        bytes(rgb565),
        mimetype="application/octet-stream"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)