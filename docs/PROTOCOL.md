# PixelLink Frame Protocol

PixelLink uses a simple TCP stream.

Each frame starts with a 16-byte network-order header:

| Offset | Size | Field |
|---:|---:|---|
| 0 | 4 | Magic: `PLNK` |
| 4 | 2 | Width |
| 6 | 2 | Height |
| 8 | 4 | Payload length |
| 12 | 4 | Frame ID |

The payload contains exactly `width × height × 2` bytes of RGB565 pixel data.

Pixels are transmitted in big-endian 16-bit order:

```
RRRR RGGG GGGB BBBB
```

The receiver must read the complete header and then exactly the advertised payload length before drawing the frame.

TCP may split a header or payload across multiple packets, so receivers must use an exact-read helper rather than assuming one `read()` returns the requested number of bytes.
