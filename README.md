# Fetch data.json from OSM
```
[out:json][timeout:25];
{{geocodeArea:"Mühlenberg, Ricklingen, Hanover, Region Hannover, Lower Saxony, Germany"}}->.a;
(
  way[highway](area.a);
  way[leisure](area.a);
  way[amenity](area.a);
  way[landuse](area.a);
  way[natural](area.a);
  way[building](area.a);
  node[natural](area.a);
  node[amenity](area.a);
);
out body;
>;
out skel qt;
```

**old:**
```
[out:json][timeout:25];
{{geocodeArea:"Mühlenberg, Ricklingen, Hanover, Region Hannover, Lower Saxony, Germany"}}->.searchArea;
(
  way["highway"](area.searchArea);
);
out body;
>;
out skel qt;
```

```
[out:json][timeout:25];
area(3604236640)->.a;
(
  way["highway"](area.a);
);
out body;
>;
out skel qt;
```

# Layers

Layer 0: surface (ways etc.)
 - Byte 1: depth into the ground (below floor height)
 - Byte 2: block type
    * `0`: default surface

    * **surface** (for highways and areas)
    * `1`: paving stones `way[surface=paving_stones]`
    * `2`: fine gravel `way[surface=fine_gravel]`
    * `3`: concrete `way[surface=concrete]`
    * `4`: asphalt `way[surface=asphalt]` or `way[highway=asphalt]`
    * `9`: dirt

    * **highway**
    * `10`: default `way[highway]`
    * `11`: footway `way[highway=footway]`
    * `12`: service `way[highway=service]`
    * `13`: cycleway `way[highway=cycleway]`
    * `14`: pedestrian `way[highway=pedestrian]`
    * `15`: residential `way[highway=residential]`
    * `16`: path `way[highway=path]`

    * **leisure**
    * `20`: default `way[leisure]`
    * `21`: park `way[leisure=park]`
    * `22`: playground `way[leisure=playground]`
    * `23`: sports centre `way[leisure=sports_centre]`
    * `24`: pitch `way[leisure=pitch]`

    * **amenity**
    * `30`: default `way[amenity]`
    * `31`: school `way[amenity=school]`
    * `32`: parking `way[amenity=parking]`

    * **landuse**
    * `40`: default `way[landuse]`
    * `41`: residential `way[landuse=residential]`
    * `42`: village green `way[landuse=village_green]`

    * **natural**
    * `50`: default `way[natural]`
    * `51`: water `way[natural=water]`

    * **underground**
    * `128 + x`: air (depth from Byte 1) with 1 block (type defined by `x`) below

Layer 1: above the surface
 - Byte 3: height
 - Byte 4: building's level count
 - Byte 5:
    * `0`: air (no wall)

    * **building**
    * `1`: default `way[building]`
    * `2`: brick `way[building:material=brick]`

    * **natural**
    * `10`: default
    * `11`: tree starts here `node[natural=tree]`
    * `12`: grass (randomly added if ground is park or village_green)

    * **amenity**
    * `21`: post box `node[amenity=post_box]`
    * `22`: recycling `node[amenity=recycling]`
    * `23`: vending machine `node[amenity=vending_machine]`
    * `24`: bench `node[amenity=bench]`
    * `25`: telephone `node[amenity=telephone]`

    * **barrier**
    * `30`: default
    * `31`: fence `way[barrier=fence]`
    * `32`: wall `way[barrier=wall]`
    * `33`: bollard `node[barrier=bollard]`
    * `34`: gate `node[barrier=gate]`
    * `35`: hedge `way[barrier=hedge]`

    * **air between**
    * 128 + x: air (height from Byte 3) with 1 stone above

# License
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
