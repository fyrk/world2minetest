minetest.set_mapgen_setting("mg_name", "singlenode", true)

local FLOOR_HEIGHT = -50

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

local SURFACE_IDS = {
    [0] = dirt, -- default
    --surface
    [1] = stone_brick, -- paving stones
    [2] = gravel, -- fine gravel
    [3] = stone, -- concrete
    [4] = obsidian, -- asphalt
    [5] = dirt, -- dirt
    -- highway
    [10] = stone, -- default
    [11] = stone, -- footway
    [12] = stone, -- service
    [13] = stone, -- cycleway
    [14] = stone, -- pedestrian
    [15] = stone, -- residential
    [16] = stone, -- path
    -- leisure
    [20] = dirt_with_grass, -- default
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
    [41] = cobblestone, -- residential_landuse
    [42] = dirt_with_grass, -- village green
    -- natural
    [50] = dirt_with_grass, -- default
    [51] = water, -- water
}

local DECORATION_IDS = {
    [0] = minetest.get_content_id("air"), -- default
    --[1] = silver_sandstone_block, -- building
    --[2] = brick, -- brick
    -- natural
    [10] = bush_leaves, -- default
    [11] = grass, -- grass
    -- trees, bushes etc.
    -- ... see DECORATION_SCHEMATICS
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

local DECORATION_SCHEMATICS = {
    [12] = {schematic=minetest.get_modpath("default") .. "/schematics/apple_tree.mts", rotation="random", force_placement=false, flags="place_center_x, place_center_z"}, -- tree
    [13] = {schematic=minetest.get_modpath("default") .. "/schematics/apple_tree.mts", rotation="random", force_placement=false, flags="place_center_x, place_center_z"}, -- leaf_tree
    [14] = {schematic=minetest.get_modpath("default") .. "/schematics/pine_tree.mts",  rotation="random", force_placement=false, flags="place_center_x, place_center_z"}, -- conifer
    [15] = {schematic=minetest.get_modpath("default") .. "/schematics/bush.mts",       rotation="random", force_placement=false, flags="place_center_x, place_center_z", shift_y=-1}, -- bush
}


local offset_x = nil
local offset_z = nil
local width = nil
local height = nil
local map = nil
local incr = nil


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

local modpath = minetest.get_modpath(minetest.get_current_modname())

local function get_layers(x, z)
    x = x + offset_x
    z = z + offset_z
    if x < 0 or z < 0 or x >= width or z >= height then
        return 0, 0, 0
    end
    local i = z*width*3 + x*3 + 1
    return bytes2int(map:sub(i, i)), bytes2int(map:sub(i+1, i+1)), bytes2int(map:sub(i+2, i+2))
end

local function load_map_file()
    local path = modpath .. "/" .. "map.dat"
    minetest.log("[w2mt] Loading map.dat from " .. path)
    local file = io.open(path, "rb")

    offset_x = bytes2int(file:read(2))
    offset_z = bytes2int(file:read(2))
    width = bytes2int(file:read(2))
    height = bytes2int(file:read(2))
    local map_size = bytes2int(file:read(4))
    map = minetest.decompress(file:read(map_size))
    local incr_size = bytes2int(file:read(4))
    incr = minetest.decompress(file:read(incr_size))
    minetest.log("[w2mt] map.dat loaded! offset_x:" .. offset_x .. " offset_z:" .. offset_z .. " width:" .. width .. " height:" .. height .. " len:" .. map:len() .. " incr mapblocks:" .. incr:len()/4)
end

load_map_file()


minetest.register_on_generated(function(minp, maxp, blockseed)
    minetest.log("[w2mt] Generating " .. minetest.pos_to_string(minp) .. " to " .. minetest.pos_to_string(maxp))

    local vm, emin, emax = minetest.get_mapgen_object("voxelmanip")
    local data = vm:get_data()
    local va = VoxelArea:new{MinEdge = emin, MaxEdge = emax}
    local schematics_to_place = {}
    for x = minp.x, maxp.x do
        for z = minp.z, maxp.z do
            local i = va:index(x, minp.y, z)
            local height, surface_id, decoration_id = get_layers(x, z)
            if x == 0 and z == 0 then
                minetest.log("(0, 0) " .. height .. " " .. surface_id .. " " .. decoration_id)
            end
            local stone_min = minp.y
            local stone_max = math.min(FLOOR_HEIGHT+height-1, maxp.y)
            local surface_y = FLOOR_HEIGHT+height
            local decoration_y = surface_y+1
            if stone_min <= stone_max then
                for _ = stone_min, stone_max do
                    data[i] = stone
                    i = i + va.ystride
                end
            end
            if minp.y <= surface_y and surface_y <= maxp.y then
                data[i] = SURFACE_IDS[surface_id]
                i = i + va.ystride
            end
            if decoration_id >= 128 then
                -- building with height decoration_id-127
                local wall_min = math.max(decoration_y, minp.y)
                local wall_max = math.min(decoration_y+decoration_id-128, maxp.y)
                if wall_min <= wall_max then
                    for _ = wall_min, wall_max do
                        data[i] = silver_sandstone_block
                        i = i + va.ystride
                    end
                end
            else
                if minp.y <= decoration_y and decoration_y <= maxp.y then
                    if 12 <= decoration_id and decoration_id <= 15 then
                        -- place tree, bush etc.
                        table.insert(schematics_to_place, {pos={x=x, y=decoration_y, z=z}, id=decoration_id})
                    else
                        data[i] = DECORATION_IDS[decoration_id]
                    end
                end
            end
        end
    end

    vm:set_data(data)
    for _, s in pairs(schematics_to_place) do
        local info = DECORATION_SCHEMATICS[s.id]
        if info.shift_y then
            s.pos.y = s.pos.y + info.shift_y
        end
        minetest.place_schematic_on_vmanip(
            vm, -- vmanip
            s.pos, -- pos
            info.schematic, -- schematic
            info.rotation, -- rotation
            info.replacement, -- replacement
            info.force_placement, -- force_placement
            info.flags -- flags
        )
    end
    vm:update_liquids()
    vm:calc_lighting()
    vm:write_to_map()
end)

minetest.register_chatcommand("w2mt:incr", {
    privs = {
        server = true
    },
    func = function(name, param)
        load_map_file()
        local len = string.len(incr)/4
        for i = 0, len-1 do
            local start_i = i*4
            local block_x = bytes2int(incr:sub(start_i+1, start_i+2), true)
            local block_z = bytes2int(incr:sub(start_i+3, start_i+4), true)
            local node_x_min = block_x * 16
            local node_x_max = node_x_min + 15
            local node_z_min = block_z * 16
            local node_z_max = node_z_min + 15
            minetest.log("[w2mt] Deleting mapblock " .. i+1 .. "/" .. len .. ": (" .. block_x .. "," .. block_z .. ") from (" .. node_x_min .. "," .. node_z_min .. ") to (" .. node_x_max .. "," .. node_z_max .. ")")
            minetest.delete_area({x=node_x_min, y=FLOOR_HEIGHT, z=node_z_min}, {x=node_x_max, y=FLOOR_HEIGHT+255, z=node_z_max})
        end
    end
})
