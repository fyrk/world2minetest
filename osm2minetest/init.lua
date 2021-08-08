local function bytes2int(str, signed) -- little endian
    -- copied from https://github.com/Gael-de-Sailly/geo-mapgen/blob/4bacbe902e7c0283a24ee3efa35c283ad592e81c/init.lua#L33
	local bytes = {str:byte(1, -1)}
	local n = 0
	local byte_val = 1
	for _, byte in ipairs(bytes) do
		n = n + (byte * byte_val)
		byte_val = byte_val * 256
	end
	if signed and n >= byte_val / 2 then
		return n - byte_val
	end
	return n
end

minetest.set_mapgen_setting("mg_name", "singlenode", true)

local FLOOR_HEIGHT = 0

local modpath = minetest.get_modpath(minetest.get_current_modname())
local file = io.open(modpath .. "/" .. "map.dat")

local offset_x = bytes2int(file:read(2))
local offset_z = bytes2int(file:read(2))
local width = bytes2int(file:read(2))
local height = bytes2int(file:read(2))
local map = minetest.decompress(file:read("a"))

minetest.log("offset_x:" .. offset_x .. " offset_z:" .. offset_z .. " width:" .. width .. " height:" .. height .. " len:" .. map:len())

local function get_layers(x, z)
    x = x + offset_x
    z = z + offset_z
    if x <= 0 or z <= 0 or x > width or z > height then
        return 0, 0, 0, 0
    end
    local i = z*width*5 + x*5 + 1
    return bytes2int(map:sub(i, i)), bytes2int(map:sub(i+1, i+1)), bytes2int(map:sub(i+2, i+2)), bytes2int(map:sub(i+3, i+3)), bytes2int(map:sub(i+4, i+4))
end


local air = minetest.get_content_id("air")
local silver_sand = minetest.get_content_id("default:silver_sand")
local dirt = minetest.get_content_id("default:dirt")
local stone = minetest.get_content_id("default:stone")
local silver_sandstone_block = minetest.get_content_id("default:silver_sandstone_block")
local stone_block = minetest.get_content_id("default:stone_block")
local stone_brick = minetest.get_content_id("default:stonebrick")
local obsidian = minetest.get_content_id("default:obsidian")
local cobblestone = minetest.get_content_id("default:cobble")
local bush_leaves = minetest.get_content_id("default:bush_leaves")
local gravel = minetest.get_content_id("default:gravel")
local dirt_with_grass = minetest.get_content_id("default:dirt_with_grass")
local sand = minetest.get_content_id("default:sand")
local desert_sand = minetest.get_content_id("default:desert_sand")
local water = minetest.get_content_id("default:water_source")
local dirt_with_dry_grass = minetest.get_content_id("default:dirt_with_dry_grass")
local gold_block = minetest.get_content_id("default:goldblock")
local copper_block = minetest.get_content_id("default:copperblock")
local steel_block = minetest.get_content_id("default:steelblock")
local diamond_block = minetest.get_content_id("default:diamondblock")
local stair = minetest.get_content_id("stairs:stair_wood")
local fence = minetest.get_content_id("default:fence_wood")
local cobblestone_wall = minetest.get_content_id("walls:cobble")
local desert_cobble_wall = minetest.get_content_id("walls:desertcobble")
local gate = minetest.get_content_id("doors:gate_wood_closed")
local grass = minetest.get_content_id("default:grass_3")
local brick = minetest.get_content_id("default:brick")

local LAYER0_IDS = {
    [0] = dirt, -- default
    --surface
    [1] = stone_brick, -- paving stones
    [2] = gravel, -- fine gravel
    [3] = stone, -- concrete
    [4] = obsidian, -- asphalt
    [9] = dirt, -- dirt
    -- highway
    [10] = cobblestone, -- default
    [11] = stone, -- footway
    [12] = stone, -- service
    [13] = stone, -- cycleway
    [14] = stone_brick, -- pedestrian
    [15] = stone, -- residential
    [16] = dirt_with_dry_grass, -- path
    -- leisure
    [20] = dirt_with_dry_grass, -- default
    [21] = dirt_with_grass, -- park
    [22] = sand, -- playground
    [23] = dirt_with_grass, -- sports centre
    [24] = desert_sand, -- pitch
    -- amenity
    [30] = stone_block, -- default
    [31] = stone_block, -- school
    [32] = stone, -- parking
    -- landuse
    [40] = dirt, -- default
    [41] = dirt, -- residential
    [42] = dirt_with_grass, -- village green
    -- natural
    [50] = dirt_with_grass, -- default
    [51] = water, -- water
}

local LAYER1_IDS = {
    [0] = minetest.get_content_id("air"), -- default
    [1] = silver_sandstone_block, -- building
    [2] = brick, -- brick
    -- natural
    [10] = bush_leaves, -- default
    --[] tree
    [12] = grass, -- grass
    -- amenity
    [21] = gold_block, -- post box
    [22] = copper_block, -- recycling
    [23] = steel_block, -- vending machine
    [24] = stair, -- bench
    [25] = diamond_block, -- telephone
    -- barrier
    [30] = cobblestone_wall, -- default
    [31] = fence, -- fence
    [32] = cobblestone_wall, -- wall
    [33] = desert_cobble_wall, -- bollard
    [34] = gate, -- gate
    [35] = bush_leaves, -- hedge
}


minetest.register_on_generated(function(minp, maxp, blockseed)
    minetest.log("[osm2minetest] Generating " .. minetest.pos_to_string(minp) .. " to " .. minetest.pos_to_string(maxp))

    local vm, emin, emax = minetest.get_mapgen_object("voxelmanip")
    local data = vm:get_data()
    local va = VoxelArea:new{MinEdge = emin, MaxEdge = emax}
    local trees_to_place = {}
    for x = minp.x, maxp.x do
        for z = minp.z, maxp.z do
            local i = va:index(x, minp.y, z)
            local l0_height, l0_id, l1_height, l1_levels, l1_id = get_layers(x, z)
            local stone_min = minp.y
            local stone_max = math.min(FLOOR_HEIGHT-l0_height-1, maxp.y)
            local l0_min =    math.max(FLOOR_HEIGHT-l0_height,   minp.y)
            local l0_max =    math.min(FLOOR_HEIGHT,             maxp.y)
            local l1_min =    math.max(FLOOR_HEIGHT+1,           minp.y)
            local l1_max =    math.min(FLOOR_HEIGHT+l1_height,   maxp.y)
            if stone_min <= stone_max then
                for _ = stone_min, stone_max do
                    data[i] = stone
                    i = i + va.ystride
                end
            end
            if l0_min <= l0_max then
                if l0_id >= 128 then
                    data[i] = LAYER0_IDS[l0_id-128]
                    i = i + va.ystride*(l0_height+1)
                else
                    local id = LAYER0_IDS[l0_id] or silver_sand
                    for _ = l0_min, l0_max do
                        data[i] = id
                        i = i + va.ystride
                    end
                end
            end
            if l1_min <= l1_max then
                if l1_id ~= 11 then
                    if l1_levels == 0 then
                        local id
                        if l1_id >= 128 then
                            i = i + va.ystride*l1_height
                            data[i] = LAYER1_IDS[l1_id-128]
                        else
                            id = LAYER1_IDS[l1_id]
                            for _ = l1_min, l1_max do
                                data[i] = id
                                i = i + va.ystride
                            end
                        end
                    else
                        local id
                        if l1_id >= 128 then
                            id = air
                        else
                            id = LAYER1_IDS[l1_id]
                        end
                        local cur_level = 1
                        local level_height = (l1_height+1)/l1_levels
                        local next_level_block = math.floor(level_height+0.5)
                        local h = 1
                        minetest.log("levels at" .. x .. " " .. z .. " : " .. l1_levels .. " h:" .. h .. " level_height:" .. level_height .. " next_level_block:" .. next_level_block)
                        for _ = l1_min, l1_max do
                            if h == next_level_block then
                                data[i] = steel_block
                                cur_level = cur_level + 1
                                next_level_block = math.floor(level_height*cur_level+0.5)
                            else
                                data[i] = id
                            end
                            i = i + va.ystride
                            h = h + 1
                        end
                        if l1_id >= 128 then
                            data[i] = LAYER1_IDS[l1_id-128]  -- roof
                        end
                    end
                else
                    -- place tree
                    table.insert(trees_to_place, {x=x, y=FLOOR_HEIGHT+1, z=z})
                end
            end
        end
    end

    vm:set_data(data)
    for _, pos in pairs(trees_to_place) do
        minetest.place_schematic_on_vmanip(
            vm, -- vmanip
            pos, -- pos
            minetest.get_modpath("default") .. "/schematics/apple_tree.mts", -- schematic
            "random", -- rotation
            nil, -- replacement
            true, -- force_placement
            "place_center_x, place_center_z" -- flags
        )
    end
    vm:update_liquids()
    vm:calc_lighting()
    vm:write_to_map()
end)
