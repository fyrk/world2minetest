import numpy as np


def to_bytes(x: int, length: int) -> bytes:
    x = [None, np.uint8, np.uint16, None, np.uint32][length](x)
    # func copied from https://github.com/Gael-de-Sailly/geo-mapgen/blob/4bacbe902e7c0283a24ee3efa35c283ad592e81c/database.py#L34
    res = x.newbyteorder("<").tobytes()
    assert len(res) == length
    return res


def from_bytes(b):
    return int.from_bytes(b, "little")



SURFACES = {
    "default": 0,

    "paving_stones": 1,
    "fine_gravel": 2,
    "concrete": 3,
    "asphalt": 4,
    "dirt": 5,

    "highway": 10,  # default
    "footway": 11,
    "service": 12,
    "cycleway": 13,
    "pedestrian": 14,
    "residential": 15,
    "path": 16,

    "leisure": 20,  # default
    "park": 21,
    "playground": 22,
    "sports_centre": 23,
    "pitch": 24,

    "amenity": 30,  # default
    "school": 31,
    "parking": 32,

    "landuse": 40,  # default
    "residential_landuse": 41,
    "village_green": 42,

    "natural": 50,  # default
    "water": 51,

    "building_ground": 60,

    "grass": 70
}

DECORATIONS = {
    "none": 0,  # air

    "natural": 10,  # default
    "grass": 11,
    "tree": 12,
    "leaf_tree": 13,
    "conifer": 14,
    "bush": 15,

    # amenity
    "post_box": 21,
    "recycling": 22,
    "vending_machine": 23,
    "bench": 24,
    "telephone": 25,

    "barrier": 30,  # default
    "fence": 31,
    "wall": 32,
    "bollard": 33,
    "gate": 34,
    "hedge": 35
}
