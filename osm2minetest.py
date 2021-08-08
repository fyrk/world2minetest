import json
import math
import random
import zlib

import numpy as np
import imageio
import skimage.draw


# position that'll be (0, ?, 0) in Minetest
# Mühlenberg:
ORIGIN_LAT = 52.34065
ORIGIN_LON = 9.69259
# Verden:
#ORIGIN_LAT = 52.92659
#ORIGIN_LON = 9.23847

# any nodes outside this area won't be used
#LAT_MIN = 52.89992
#LON_MIN = 9.19803
#LAT_MAX = 52.94557
#LON_MAX = 9.27279
LAT_MIN = 52
LON_MIN = 9
LAT_MAX = 53
LON_MAX = 10


assert LAT_MIN <= ORIGIN_LAT <= LAT_MAX
assert LON_MIN <= ORIGIN_LON <= LON_MAX


def coord_distance(lat1, lon1, lat2, lon2):
    # from https://www.movable-type.co.uk/scripts/latlong.html
    R = 6371e3 # metres
    φ1 = lat1 * math.pi/180 # φ, λ in radians
    φ2 = lat2 * math.pi/180
    Δφ = (lat2-lat1) * math.pi/180
    Δλ = (lon2-lon1) * math.pi/180

    a = (math.sin(Δφ/2) * math.sin(Δφ/2) +
         math.cos(φ1) * math.cos(φ2) *
         math.sin(Δλ/2) * math.sin(Δλ/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c # in metres


def degrees2pos(lat, lon):
    x = int(round(coord_distance(ORIGIN_LAT, ORIGIN_LON, ORIGIN_LAT, lon)))
    y = int(round(coord_distance(ORIGIN_LAT, ORIGIN_LON, lat, ORIGIN_LON)))
    if lon < ORIGIN_LON:
        x = -x
    if lat < ORIGIN_LAT:
        y = -y
    return x, y


def nodes2positions(node_ids):
    x_coords = []
    y_coords = []
    for node_id in node_ids:
        node = nodes_by_id.get(node_id)
        if node:
            x, y = degrees2pos(node["lat"], node["lon"])
            x_coords.append(x-min_x)
            y_coords.append(y-min_y)
    return x_coords, y_coords


def print_element(msg, e):
    print(msg, f"{e['id']} {e['type']}[{','.join(k+'='+v for k,v in e.get('tags', {}).items())}]")


min_lat = ORIGIN_LAT
max_lat = ORIGIN_LAT
min_lon = ORIGIN_LON
max_lon = ORIGIN_LON


with open("data.json", "r") as f:
    data = json.load(f)

nodes_by_id = {}

highways = []
buildings = []
areas = []
barriers = []
nodes = []

# sort elements by type (highway, building, area or node)
for e in data["elements"]:
    t = e["type"]
    tags = e.get("tags")
    if t == "way":
        if not tags:
            print_element("Ignored, missing tags:", e)
            continue
        if "area" in tags:
            areas.append(e)
        elif "highway" in tags:
            highways.append(e)
        elif "building" in tags or "building:part" in tags:
            buildings.append(e)
        elif "barrier" in tags:
            barriers.append(e)
        else:
            areas.append(e)
    elif t == "node":
        lat = e["lat"]
        lon = e["lon"]
        if LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX:
            nodes_by_id[e["id"]] = e
            min_lat = min(min_lat, lat)
            max_lat = max(max_lat, lat)
            min_lon = min(min_lon, lon)
            max_lon = max(max_lon, lon)
            if tags and ("natural" in tags or "amenity" in tags or "barrier" in tags):
                nodes.append(e)
    else:
        print(f"Ignoring element with unknown type '{t}'")


min_x, min_y = degrees2pos(min_lat, min_lon)
max_x, max_y = degrees2pos(max_lat, max_lon)

print(f"from {min_lat},{min_lon} to {max_lat},{max_lon}")
print(f"from {min_x},{min_y} to {max_x},{max_y} (size: {max_x-min_x+1},{max_y-min_y+1})")

a = np.zeros((max_y-min_y+1, max_x-min_x+1, 5), dtype="uint8")  # 4 bytes per block, see README.md for format
layers = np.zeros((max_y-min_y+1, max_x-min_x+1), dtype="uint8")

print("AREAS")
for area in areas:
    tags = area["tags"]
    id_ = None
    if "surface" in tags:
        id_ = {
            "paving_stones": 1,
            "fine_gravel": 1,
            "concrete": 3,
            "asphalt": 4
        }.get(tags["surface"])
    if id_ is None:
        if "natural" in tags:
            if tags["natural"] == "water":
                id_ = 51
            else:
                id_ = 50
        elif "amenity" in tags:
            id_ = {
                "school": 31,
                "parking": 32
            }.get(tags["amenity"], 30)
        elif "leisure" in tags:
            id_ = {
                "park": 21,
                "playground": 22,
                "sports_centre": 23,
                "pitch": 24
            }.get(tags["leisure"], 20)
        elif "landuse" in tags:
            id_ = {
                "residential": 41,
                "village_green": 42
            }.get(tags["landuse"], 40)
    if id_ is None:
        print_element("Ignored area without id:", area)
        continue
    x_coords, y_coords = nodes2positions(area["nodes"])
    if id_ == 51:
        print("water at", x, y)
    xx, yy = skimage.draw.polygon(x_coords, y_coords)
    a[yy, xx, 0] = 0 if id_ != 51 else 3  # water is 3 nodes deep
    a[yy, xx, 1] = id_
    if id_ == 21 or id_ == 42:  # park or village_green
        # add a bit of random grass
        random.seed(area["id"])
        for x, y in zip(xx, yy):
            if random.random() < 0.025:
                a[y, x, 2] = 1  # height is 1
                a[y, x, 4] = 12  # grass
    else:
        a[yy, xx, 2] = 0  # if areas overlap, this removes any randomly generated grass


print("BUILDINGS")
for building in buildings:
    x_coords, y_coords = nodes2positions(building["nodes"])
    if len(x_coords) < 2:
        print_element(f"Ignored, only {len(x_coords)} nodes:", building)
    tags = building["tags"]
    id_ = 1
    if "building:material" in tags:
        id_ = {
            "brick": 2
        }.get(tags["building:material"], 1)
        if id_ == 1:
            print_element("Unrecognized building:material", building)
    building_height = -1
    levels = 0
    is_building_part = "building:part" in tags
    try:
        levels = int(tags["building:levels"])
    except (KeyError, ValueError):
        pass
    try:
        building_height = int(float(tags["height"]))
    except (KeyError, ValueError):
        if levels != 0:
            building_height = levels*3
    building_height = min(building_height, 255)
    if len(x_coords) == 2:
        xx, yy = skimage.draw.line(x_coords[0], y_coords[0], x_coords[1], y_coords[1])
    else:
        if id_ == 1 and building_height != -1:
            # roof for buildings
            xx, yy = skimage.draw.polygon(x_coords, y_coords)
            if not is_building_part:
                a[yy, xx, 2] = np.maximum(a[yy, xx, 2], building_height)
            else:
                # only overwrite height if it is likely from the same building
                a[yy, xx, 2] = building_height
            a[yy, xx, 3] = np.maximum(a[yy, xx, 3], levels)
            a[yy, xx, 4] = np.where(a[yy, xx, 4]==0, id_ + 128, a[yy, xx, 4])  # do not overwrite walls
        xx, yy = skimage.draw.polygon_perimeter(x_coords, y_coords)
    if building_height == -1:
        building_height = 1
    a[yy, xx, 2] = np.maximum(a[yy, xx, 2], building_height)
    a[yy, xx, 3] = np.maximum(a[yy, xx, 3], levels)
    a[yy, xx, 4] = id_


print("BARRIERS")
for barrier in barriers:
    id_ = {
        "fence": 31,
        "wall": 32,
        "hedge": 35
    }.get(barrier["tags"]["barrier"], 30)
    height = 1
    if id_ == 35:
        height = 2
    if id_ == 30:
        print_element("Default barrier:", barrier)
    x_coords, y_coords = nodes2positions(barrier["nodes"])
    for i in range(0, len(x_coords)-1):
        x1, y1 = x_coords[i], y_coords[i]
        x2, y2 = x_coords[i+1], y_coords[i+1]
        xx, yy = skimage.draw.line(x1, y1, x2, y2)
        a[yy, xx, 2] = height
        a[yy, xx, 4] = id_


print("HIGHWAYS")
for highway in highways:
    tags = highway["tags"]
    id_ = 10
    width = 3
    value = tags["highway"]
    if value == "asphalt":
        id_ = 5
    elif value == "footway":
        id_ = 11
        width = 3
    elif value == "service":
        id_ = 12
        width = 4
    elif value == "cycleway":
        id_ = 13
        width = 3
    elif value == "pedestrian":
        id_ = 14
        width = 3
    elif value == "residential":
        id_ = 15
        width = 5  # both sides
    elif value == "path":
        id_ = 16
        width = 1
    elif value == "primary":
        width = 6
    elif value == "secondary":
        width = 6
    if "surface" in tags:
        id_ = {
            "paving_stones": 1,
            "fine_gravel": 2,
            "concrete": 3,
            "asphalt": 4
        }.get(tags["surface"], id_)
    if id_ == 10:
        print_element("Default highway:", highway)
    
    layer = tags.get("layer", 0)
    try:
        layer = int(layer)
    except ValueError:
        layer = 0
    if "tunnel" in tags and tags["tunnel"] != "building_passage":
        if "layer" in tags:
            try:
                layer = int(tags["layer"])
            except ValueError:
                layer = -1
            if layer > 0:
                layer = 0
        else:
            layer = -1
    height = abs(layer)*3
    if layer < 0:
        id_ += 128

    x_coords, y_coords = nodes2positions(highway["nodes"])
    for i in range(0, len(x_coords)-1):
        x1, y1 = x_coords[i], y_coords[i]
        x2, y2 = x_coords[i+1], y_coords[i+1]
        xx, yy = skimage.draw.line(x1, y1, x2, y2)
        if width != 1:
            # very naive implementation for widths, improvement needed
            positions = set()
            if width == 3:
                for x, y in zip(xx, yy):
                    positions.update((
                                (x, y+1),
                        (x-1, y), (x, y  ), (x+1, y),
                                (x, y-1)
                    ))
            elif width == 4:
                for x, y in zip(xx, yy):
                    positions.update((
                        (x-1, y+1), (x, y+1), (x+1, y+1),
                        (x-1, y  ), (x, y  ), (x+1, y  ),
                        (x-1, y-1), (x, y-1), (x+1, y-1)
                    ))
            elif width == 5:
                for x, y in zip(xx, yy):
                    positions.update((
                                              (x, y+2),
                                  (x-1, y+1), (x, y+1), (x+1, y+1),
                        (x-2, y), (x-1, y  ), (x, y  ), (x+1, y  ), (x+2, y  ),
                                  (x-1, y-1), (x, y-1), (x+1, y-1),
                                              (x, y+1)
                    ))
            xx = []
            yy = []
            for x, y in positions:
                xx.append(x)
                yy.append(y)
        a[yy, xx, 0] = height
        a[yy, xx, 1] = id_
        if layer >= 0:
            a[yy, xx, 2] = 0  # remove anything above the surface (buildings, randomly added grass)


# NODES
for node in nodes:
    tags = node["tags"]
    id_ = None
    height = 1
    if "natural" in tags:
        if tags["natural"] == "tree":
            id_ = 11
            try:
                height = int(tags["height"])
            except (KeyError, ValueError):
                height = 5
        else:
            id_ = 10
            print_element("Default natural node:", node)
    elif "amenity" in tags:
        id_ = {
            "post_box": 21,
            "recycling": 22,
            "vending_machine": 23,
            "bench": 24,
            "telephone": 25
        }.get(tags["amenity"])
        if tags["amenity"] == "bench":
            height = 1
        else:
            height = 2
    elif "barrier" in tags:
        id_ = {
            "bollard": 33,
            "gate": 34
        }.get(tags["barrier"], 30)
        if id_ == 30:
            print_element("Default barrier:", node)
    if id_ is None:
        print_element("Ignored node without id:", node)
        continue
    x, y = degrees2pos(node["lat"], node["lon"])
    x = x-min_x
    y = y-min_y
    a[y, x, 2] = height
    a[y, x, 4] = id_
    if id_ == 11:
        # place dirt below tree
        a[y, x, 0] = 0  # on surface
        a[y, x, 1] = 9  # dirt


print(f"from {min_lat},{min_lon} to {max_lat},{max_lon}")
print(f"from {min_x},{min_y} to {max_x},{max_y} (size: {max_x-min_x+1},{max_y-min_y+1})")


def le(x):
    # func copied from https://github.com/Gael-de-Sailly/geo-mapgen/blob/4bacbe902e7c0283a24ee3efa35c283ad592e81c/database.py#L34
    return x.newbyteorder("<").tobytes()


with open("osm2minetest/map.dat", "wb") as f:
    f.write(le(np.uint16(-min_x)))
    f.write(le(np.uint16(-min_y)))
    f.write(le(np.uint16(a.shape[1])))
    f.write(le(np.uint16(a.shape[0])))
    f.write(zlib.compress(a.tobytes(), 9))

for i in range(4):
    layer = a[::-1,:,i]
    name = "layer" + ["0_height", "0_id", "1_height", "1_id"][i]
    m = max(layer.max(), 1)
    print(name, "max value:", m)
    imageio.imwrite(f"osm2minetest/{name}.png", layer*int(255/m))
