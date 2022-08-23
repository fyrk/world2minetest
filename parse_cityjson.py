import argparse
import os.path
from functools import partial

import raster_geometry as rg
from cjio import cityjson
from tqdm import tqdm

from _util import to_bytes


parser = argparse.ArgumentParser(description="Parse CityJSON .json files and create a buildings file for generate_map.py")
parser.add_argument("files", metavar="file", type=str, nargs="+", help=".json files to process")
parser.add_argument("--fill", action="store_true", help="Fill the building's polygons instead of only drawing the outlines. This is much slower and doesn't work correctly for concave polygons. Roofs are always filled.")
parser.add_argument("--output", "-o", type=argparse.FileType("wb"), help="Output file. Defaults to parsed_data/buildings_cityjson.dat", default="./parsed_data/buildings_cityjson.dat")

args = parser.parse_args()

polygon = rg.bresenham_polygon
lines = partial(rg.bresenham_lines, closed=True)
get_polygon_points_normal = polygon if args.fill else lines
get_polygon_points_roof = polygon

buildings = []

for filepath in args.files:
    print(os.path.basename(filepath))
    cm = cityjson.load(filepath)
    for co in cm.cityobjects.values():
        if co.type.lower() not in ["building", "buildingpart", "buildinginstallation"]:
            print("Ignoring", co.type, co)
    t = tqdm(cm.get_cityobjects(type=["building", "buildingpart", "buildinginstallation"]).values())
    for building in t:
        t.set_description(building.id)
        if len(building.geometry) >= 1:
            assert len(building.geometry) == 1
            geom = building.geometry[0]
            res_building = {}
            for surface in geom.surfaces.values():
                type_ = {
                    "WallSurface": "wall",
                    "RoofSurface": "roof",
                    "GroundSurface": "ground"
                }.get(surface["type"], "other")
                if type_ == "other":
                    print(f"unknown surface type '{surface['type']}'")
                
                get_points = get_polygon_points_roof if type_ == "roof" else get_polygon_points_normal

                boundaries = []
                for x in geom.get_surfaces(type=surface["type"]).values():
                    boundaries.append(geom.get_surface_boundaries(x))
                surface_points = set()
                for composite in boundaries:
                    for shell in composite:
                        for boundary in shell:
                            rg.bresenham_lines
                            surface_points.update(get_points([tuple(int(round(x)) for x in pos) for pos in boundary]))
                
                res_building[type_] = list(surface_points)
            buildings.append(res_building)


with args.output as f:
    f.write(to_bytes(len(buildings), 4))
    for building in buildings:
        f.write(to_bytes(0, 1))
        for surface_name, points in building.items():
            surface_name = surface_name.encode("utf-8")
            f.write(to_bytes(len(surface_name), 1))
            f.write(surface_name)
            f.write(to_bytes(len(points), 4))
            for point in points:
                for coord in point:
                    f.write(to_bytes(coord, 4))
