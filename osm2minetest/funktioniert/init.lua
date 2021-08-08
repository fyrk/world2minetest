minetest.set_mapgen_setting("mg_name", "singlenode", true)

local FLOOR_HEIGHT = 0

local modpath = minetest.get_modpath(minetest.get_current_modname())
local file = io.open(modpath .. "/" .. "map.dat")
local width = file:read("n")
local height = file:read("n")
file:read(1)  -- space after height
local ways = file:read("a")

minetest.log("width is " .. width .. " height is " .. height .. " len is " .. ways:len() .. " start of ways is " .. ways:sub(1, 100))

local function get_build_height(x, z)
    if x <= 0 or z <= 0 or x > width or z > height then
        return 0
    end
    local i = z*width+x
    return tonumber(ways:sub(i, i))
end

minetest.register_on_generated(function(minp, maxp, blockseed)
    minetest.log("[osm2minetest] Generating " .. minetest.pos_to_string(minp) .. " to " .. minetest.pos_to_string(maxp) .. " width is " .. width .. " height is " .. height .. " len is " .. ways:len())

    local stone_id = minetest.get_content_id("default:stone")
    local grass_id = minetest.get_content_id("default:dirt_with_grass")

    local vm, emin, emax = minetest.get_mapgen_object("voxelmanip")
    local data = vm:get_data()
    local va = VoxelArea:new{MinEdge = emin, MaxEdge = emax}
    for x = minp.x, maxp.x do
        for z = minp.z, maxp.z do
            local i = va:index(x, minp.y, z)
            local stone_min = minp.y
            local stone_max = math.min(FLOOR_HEIGHT-1, maxp.y)
            if stone_min <= stone_max then
                for _ = stone_min, stone_max do
                    data[i] = stone_id
                    i = i + va.ystride
                end
            end
            if minp.y <= FLOOR_HEIGHT and maxp.y >= FLOOR_HEIGHT then
                local h = get_build_height(x, z)
                if h == 0 then
                    data[i] = grass_id
                else
                    for _ = 1, h do
                        data[i] = stone_id
                        i = i + va.ystride
                    end
                end
            end
        end
    end

    vm:set_data(data)
    vm:calc_lighting()
    vm:write_to_map()
end)
