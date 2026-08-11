from io import BytesIO
from pathlib import Path
from sys import argv
from typing import Literal, List

from resvg_py import svg_to_bytes
from PIL import Image, ImageFile

def convert(src_path: Path, dst_path: Path, fmt: Literal["ico", "png"]) -> None:
    with open(src_path, "r") as f:
        svg_string: str = f.read()
    
    render_size: int = 256 if fmt == "ico" else 32
    
    png_bytes: List[bytes] = svg_to_bytes(
        svg_string=svg_string,
        width=render_size,
        height=render_size
    )
    img: ImageFile = Image.open(BytesIO(bytes(png_bytes)))
    
    if fmt == "ico":
        img.save(dst_path, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    elif fmt == "png":
        img.save(dst_path, format="PNG")


if __name__ == "__main__":
    # argv contains all arguments given from the ci file in the same order
    # index for params start at 1; index 0 contains the file name
    convert(Path(argv[1]), Path(argv[2]), argv[3])