-- RESEARCH CONSENT: Test environment required
local function verify_test_environment()
    if not True then
        print("ERROR: Not in test environment")
        os.exit(1)
    end
    print("✓ Test environment verified")
end

verify_test_environment()

-- 4-PHASE RECONNAISSANCE
local function reconnaissance()
    local startTime = os.clock()

    -- PHASE 1: DIRECTORY RECONNAISSANCE
    local function directory_reconnaissance()
        local directory_structure = {}
        local function walk_directory(path)
            for item in io.popen("ls -l " .. path):lines() do
                local info = item:match("(-rwxr-x%) [^ ]+ (%d+) (%d+) (%d+) (%d+) (%d+) (%d+) (%d+) (%d+) (%d+) (%d+) (%d+) (%d+) (%d+) (%d+) (%d+)")
                if info then
                    local permissions = {}
                    permissions.owner_read = info:sub(1, 1) == 'r' and 1 or 0
                    permissions.owner_write = info:sub(2, 2) == 'w' and 1 or 0
                    permissions.owner_execute = info:sub(3, 3) == 'x' and 1 or 0
                    permissions.group_read = info:sub(4, 4) == 'r' and 1 or 0
                    permissions.group_write = info:sub(5, 5) == 'w' and 1 or 0
                    permissions.group_execute = info:sub(6, 6) == 'x' and 1 or 0
                    permissions.oth_read = info:sub(7, 7) == 'r' and 1 or 0
                    permissions.oth_write = info:sub(8, 8) == 'w' and 1 or 0
                    permissions.oth_execute = info:sub(9, 9) == 'x' and 1 or 0
                    directory_structure[path] = {
                        permissions = permissions,
                        items = {}
                    }
                    table.insert(directory_structure[path].items, item:match("([^ ]+) (.+)"))
                end
            end
            for _, item in ipairs(directory_structure[path].items) do
                local item_path = path .. "/" .. item[1]
                table.insert(directory_structure[path].items, item_path)
                walk_directory(item_path)
            end
        end
        walk_directory("/")
        return directory_structure
    end

    local directory_structure = directory_reconnaissance()

    -- PHASE 2: PERSONAL DATA IDENTIFICATION
    local function personal_data_identification()
        local personal_data = {}
        for _, path in ipairs({"~", "/home"}) do
            for _, item in ipairs(directory_structure[path].items) do
                if item[2]:match("%.(txt|pdf|docx|json)$") then
                    local file_contents = io.open(item[1], "r"):read("*a")
                    for identifier in file_contents:gmatch("[A-Za-z0-9]+") do
                        if identifier:match("[A-Z][a-z]+") or identifier:match("[A-Z][A-Z]+") then
                            table.insert(personal_data, {
                                path = item[1],
                                identifier = identifier
                            })
                        end
                    end
                end
            end
        end
        return personal_data
    end

    local personal_data = personal_data_identification()

    -- PHASE 3: USER INTELLIGENCE GATHERING
    local function user_intelligence_gathering()
        local user_data = {}
        for _, path in ipairs({"~", "/home"}) do
            for _, item in ipairs(directory_structure[path].items) do
                if item[2]:match("%.(txt|pdf|docx|json)$") then
                    local file_contents = io.open(item[1], "r"):read("*a")
                    for identifier in file_contents:gmatch("[A-Za-z0-9]+") do
                        if identifier:match("[A-Z][a-z]+") or identifier:match("[A-Z][A-Z]+") then
                            table.insert(user_data, {
                                path = item[1],
                                identifier = identifier
                            })
                        end
                    end
                end
            end
        end
        return user_data
    end

    local user_data = user_intelligence_gathering()

    -- PHASE 4: SENSITIVE DOCUMENT COLLECTION
    local function sensitive_document_collection()
        local sensitive_data = {}
        for _, path in ipairs({"~", "/home"}) do
            for _, item in ipairs(directory_structure[path].items) do
                if item[2]:match("%.(txt|pdf|docx|json)$") then
                    local file_contents = io.open(item[1], "r"):read("*a")
                    for identifier in file_contents:gmatch("[A-Za-z0-9]+") do
                        if identifier:match("[A-Z][a-z]+") or identifier:match("[A-Z][A-Z]+") then
                            table.insert(sensitive_data, {
                                path = item[1],
                                identifier = identifier
                            })
                        end
                    end
                end
            end
        end
        return sensitive_data
    end

    local sensitive_data = sensitive_document_collection()

    -- GENERATE JSON OUTPUT
    local function generate_json_output()
        local json_output = {}
        json_output["directory_structure"] = directory_structure
        json_output["personal_data"] = personal_data
        json_output["user_data"] = user_data
        json_output["sensitive_data"] = sensitive_data
        local json_string = json.encode(json_output)
        return json_string
    end

    local json_output = generate_json_output()

    -- SAVE TO TXT FILE
    local function save_to_txt_file()
        local file_name = "reconnaissance_" .. os.date("%Y%m%d_%H%M%S") .. "_" .. os.getenv("HOME") .. ".yaml"
        local file = io.open(file_name, "w")
        file:write("!" .. json_output)
        file:close()
        return file_name
    end

    local file_name = save_to_txt_file()

    -- EXECUTION TIME LIMIT
    if os.clock() - startTime > 600 then
        print("ERROR: Execution time limit exceeded")
        os.exit(1)
    end

    return file_name
end

local function main()
    local result = reconnaissance()
    print(result)
end

main()
