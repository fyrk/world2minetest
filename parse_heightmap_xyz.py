import argparse
import os.path
import zlib

import numpy as np
from scipy.ndimage import median_filter

from _util import to_bytes

parser = argparse.ArgumentParser(description="Parse DGM1 'XYZ ASCII' files and generate a heightmap")
parser.add_argument("files", metavar="file", type=argparse.FileType("r", encoding="utf-8"), nargs="+", help=".xyz files to process")
parser.add_argument("--output", "-o", type=argparse.FileType("wb"), help="Output file. Defaults to parsed_data/heightmap.dat", default="./parsed_data/heightmap.dat")
parser.add_argument("--medfiltsize", type=int, help="Odd kernel_size integer for scipy.ndimage.median_filter to smoothen the heights. 0 to disable. Defaults to 5.", default=5)
parser.add_argument("--createimg", action="store_true", help="Create a .png visualization of the heightmap")

args = parser.parse_args()

heights = []
for file in args.files:
    print(os.path.basename(file.name))
    for line in file.readlines():
        x, y, z = (float(f) for f in line.split())
        heights.append((int(x), int(y), int(round(z))))
    file.close()

heights_xy = [(x, y) for x, y, _ in heights]
min_pos = min(heights_xy)
max_pos = max(heights_xy)
z_values = [z for _, _, z in heights]
min_height = min(z_values)
max_height = max(z_values)
size = (max_pos[0]-min_pos[0]+1, max_pos[1]-min_pos[1]+1)
print("min:", min_pos, "height:", min_height)
print("max:", max_pos, "height:", max_height)
print("size:", size)

min_x, min_y = min_pos
a = np.empty((size[1], size[0]), dtype=np.uint8)
for x, y, z in heights:
    a[y-min_y, x-min_x] = z

if args.medfiltsize:
    print(a.min())
    a = median_filter(a, (args.medfiltsize, args.medfiltsize))
    print(a.min())

out = args.output
out.write(to_bytes(min_x, 4))
out.write(to_bytes(min_y, 4))
out.write(to_bytes(size[0], 2))
out.write(to_bytes(size[1], 2))
out.write(zlib.compress(a.tobytes(), 9))
print("heightmap", a)
if args.createimg:
    print("Writing image...")
    import imageio
    imageio.imwrite(out.name + ".png", (a[::-1]-min_height)*int(255/(max_height-min_height)))
