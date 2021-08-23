import argparse
import json
import os.path
from collections import defaultdict

import numpy as np
import ezdxf

from _util import SURFACES, DECORATIONS

parser = argparse.ArgumentParser(description="Parse SKH1000 .dxf files and generate JSON data containing features")
parser.add_argument("files", metavar="file", type=str, nargs="+", help=".dxf files to process")
parser.add_argument("--output", "-o", type=argparse.FileType("w"), help="Output file. Defaults to parsed_data/features_dxf.json", default="./parsed_data/features_dxf.json")
parser.add_argument("--query", "-q", action="append", nargs=2, metavar=("query", "decoration-name"), help="ezdxf query, followed by the decoration name id ('tree', 'bush', etc.)")

args = parser.parse_args()

decorations = defaultdict(list)

for filepath in args.files:
    print(os.path.basename(filepath))
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()
    for query, deco in args.query:
        entities = msp.query(query)
        print(f"  {deco}: {len(entities)} entities found")
        if entities:
            decorations[deco].extend({"x": int(round(e.dxf.insert[0])), "y": int(round(e.dxf.insert[1]))} for e in entities)

min_x = min(d["x"] for ds in decorations.values() for d in ds)
min_y = min(d["y"] for ds in decorations.values() for d in ds)
max_x = max(d["x"] for ds in decorations.values() for d in ds)
max_y = max(d["y"] for ds in decorations.values() for d in ds)

json.dump({
    "min_x": min_x,
    "max_x": max_x,
    "min_y": min_y,
    "max_y": max_y,
    "decorations": decorations
}, args.output, indent=2)
