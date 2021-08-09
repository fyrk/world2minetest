**This is still work in progress**

world2minetest is a tool to generate [Minetest](https://www.minetest.net/) worlds based on publicly available real-world geodata. It was inspired by tools such as [geo-mapgen](https://github.com/Gael-de-Sailly/geo-mapgen).

Currently, the following geodata sources are supported:
 * Heightmaps in "XYZ ASCII" format in a [EPSG:25832](https://epsg.io/25832) coordinate system ([example](https://www.hannover.de/Leben-in-der-Region-Hannover/Verwaltungen-Kommunen/Die-Verwaltung-der-Landeshauptstadt-Hannover/Dezernate-und-Fachbereiche-der-LHH/Stadtentwicklung-und-Bauen/Fachbereich-Planen-und-Stadtentwicklung/Geoinformation/Open-GeoData/3D-Stadtmodell-und-Gel%C3%A4ndemodell/Digitales-Gel%C3%A4ndemodell-DGM1))
 * [OpenStreetMap](https://openstreetmap.org), using the [Overpass API](https://overpass-turbo.eu/)
 * .dxf CAD files (trees only)

Installation
============

 1. Copy this repo's content to your computer, e.g. by cloning:
    ```
    git clone https://github.com/FlorianRaediker/world2minetest.git
    ```
 2. Install the required Python modules:
    ```
    pip3 install -r requirements.txt
    ```

How to use
==========
Generating a Minetest world currently consists of the following 4 steps. Either step 1, step 2, or step3 is required.

 1. Generate a heightmap.
 2. Use OpenStreetMap data to add details.
 3. Add trees using .dxf data.
 4. Create a `map.dat` file that can be read by world2minetest Mod for Minetest.

## Generating a heightmap
A heightmap can be generated using the parse_heightmap_dgm.py script. See `python3 parse_heightmap_dgm.py -h` for details.
First, download ASCII XYZ files and save them to the `data_sources/` directory.

For Hanover (Germany), you can use this link: https://www.hannover.de/Leben-in-der-Region-Hannover/Verwaltungen-Kommunen/Die-Verwaltung-der-Landeshauptstadt-Hannover/Dezernate-und-Fachbereiche-der-LHH/Stadtentwicklung-und-Bauen/Fachbereich-Planen-und-Stadtentwicklung/Geoinformation/Open-GeoData/3D-Stadtmodell-und-Gel%C3%A4ndemodell/Digitales-Gel%C3%A4ndemodell-DGM1.

Then, call parse_dgm.py with any files you want to convert into a heightmap:
```
$ python3 parse_dgm.py data_sources/path/to/file1.xyz data_sources/path/to/file2.xyz ...
```
This will create a new file `parsed_data/heightmap.dat`

## Use OpenStreetMap data
Select data using the [Overpass API](https://overpass-turbo.eu/). 
Here is an example query:
```
[out:json][timeout:25][bbox:{{bbox}}];
(
   way;
   node;
);
out body;
>;
out skel qt;
```

Copy the JSON data from the "Data" tab into a file `data_sources/osm.json`.
Then, parse this data with parse_osm.py (see `python3 parse_features_osm.py -h` for details).
```
$ python3 parse_osm.py data_sources/osm.json
```
This will create a new file `parsed_data/features_osm.json`.

## Add trees from .dxf files
For geodata saved in .dxf files, parse_features_dxf.py can be used (see `python3 parse_features_dxf.py -h` for details).
Currently, only trees are supported.
You will want to specify a query for [ezdxf](https://ezdxf.readthedocs.io/en/stable/tutorials/getting_data.html#retrieve-entities-by-query-language) to get all entities representing trees.
Example command:
```
$ python3 parse_features_dxf.py data_sources/path/to/file1.xyz data_sources/path/to/file2.xyz ... --tree-query="*[(layer=='Eingemessene Bäume' & name=='S220.40']"
```

## Putting it all together – creating `map.dat`
See `python3 generate_map.py` for details.
Example usage:
```
$ python3 generate_map.py --heightmap=parsed_data/heightmap.dat --features=parsed_data/features_osm.json --features=parsed_data/features_dxf.json
```

Screenshots
===========
![](docs/screenshot_water.png)
![](docs/screenshot_trees_with_postboxes_and_buildings.png)
![](docs/screenshot_bench.png)
![](docs/screenshot_fence.png)
![](docs/screenshot_primary_road.png)


License
=======
world2minetest - Generate Minetest worlds based on geodata<br>
Copyright (C) 2021  Florian Rädiker

This program is free software: you can redistribute it and/or modify<br>
it under the terms of the GNU Affero General Public License as published<br>
by the Free Software Foundation, either version 3 of the License, or<br>
(at your option) any later version.

This program is distributed in the hope that it will be useful,<br>
but WITHOUT ANY WARRANTY; without even the implied warranty of<br>
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the<br>
GNU Affero General Public License for more details.<br>

You should have received a copy of the GNU Affero General Public License<br>
along with this program.  If not, see <https://www.gnu.org/licenses/>.
