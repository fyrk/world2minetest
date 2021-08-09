import argparse
import json
import os.path

import numpy as np
import ezdxf

from _util import SURFACES, DECORATIONS

parser = argparse.ArgumentParser(description="Parse SKH1000 .dxf files and generate JSON data containing features")
parser.add_argument("files", metavar="file", type=str, nargs="+", help=".dxf files to process")
parser.add_argument("--output", "-o", type=argparse.FileType("w"), help="Output file. Defaults to parsed_data/features_dxf.json", default="./parsed_data/features_dxf.json")
parser.add_argument("--tree-query", help="ezdxf query for trees")

args = parser.parse_args()

tree_positions = []

print("query", repr(args.tree_query))
for filepath in args.files:
    print(os.path.basename(filepath))
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()
    if args.tree_query:
        tree_entities = msp.query(args.tree_query)
        if tree_entities:
            tree_positions.extend((int(round(t.dxf.insert[0])), int(round(t.dxf.insert[1]))) for t in tree_entities)
        else:
            print("No trees found")

decorations = [{"x": p[0], "y": p[1], "type": "tree"} for p in tree_positions]

min_x = min(p[0] for p in tree_positions)
min_y = min(p[1] for p in tree_positions)
max_x = max(p[0] for p in tree_positions)
max_y = max(p[1] for p in tree_positions)

json.dump({
    "min_x": min_x,
    "max_x": max_x,
    "min_y": min_y,
    "max_y": max_y,
    "decorations": decorations
}, args.output, indent=2)
