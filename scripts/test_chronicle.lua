-- Tests for Lua Neovim script for Chronicle.
-- Run with: `lua scripts/test_chronicle.lua`.

local luaunit = require('luaunit')
local chronicle = require("chronicle")

-- Mock Vim API.
local mock_vim = {
    buffer = {},  -- Simulated buffer content.
    cursor = {1, 0},  -- Simulated cursor position.
}

-- Mock the functions that interact with Vim.

chronicle.replace = function(line)
    mock_vim.buffer[mock_vim.cursor[1]] = line
end

chronicle.insert = function(line)
    table.insert(mock_vim.buffer, mock_vim.cursor[1] + 1, line)
end

chronicle.insert_at = function(line, line_number)
    if line_number > #mock_vim.buffer then
        table.insert(mock_vim.buffer, line)
    else
        table.insert(mock_vim.buffer, line_number + 1, line)
    end
end

chronicle.notify = function(message)
    print(message)
end

chronicle.get_all_lines = function()
    return mock_vim.buffer
end

chronicle.get_cursor_line = function()
    return mock_vim.cursor[1]
end

chronicle.get_current_line = function()
    return mock_vim.buffer[mock_vim.cursor[1]]
end

chronicle.now = function()
    return "12:34"
end

-- Helper to simulate cursor movement.
local function set_cursor(line, column)
    mock_vim.cursor = {line, column or 0}
end

-- Helper to get current line.
local function get_current_line()
    return mock_vim.buffer[mock_vim.cursor[1]]
end

local function compare(expected, actual)
    luaunit.assertEquals(#expected, #actual, "Buffer length mismatch")
    for i, line in ipairs(expected) do
        luaunit.assertEquals(line, actual[i], "Line " .. i .. " mismatch")
    end
end

-- Test suite
TestChronicle = {}  -- Make it global so luaunit can find it

function TestChronicle:setUp()
    -- Reset mock buffer before each test
    mock_vim.buffer = {}
end

function TestChronicle:test_start_event()
    mock_vim.buffer = {
        "2024-01-01",
        "",
        "program @chronicle"
    }
    set_cursor(3)

    chronicle.start()
    luaunit.assertEquals(
        "    12:34/      program @chronicle",
        get_current_line()
    )
end

function TestChronicle:test_start_task()
    mock_vim.buffer = {
        "2024-01-01",
        "",
        "[ ] program @chronicle"
    }
    set_cursor(3)

    chronicle.start()
    luaunit.assertEquals(
        "[ ] 12:34/      program @chronicle",
        get_current_line()
    )
end

function TestChronicle:test_finish_event()
    mock_vim.buffer = {
        "2024-01-01",
        "",
        "12:33/ program @chronicle"
    }
    set_cursor(3)

    chronicle.finish()
    luaunit.assertEquals(
        "    12:33/12:34 program @chronicle",
        get_current_line()
    )
end

function TestChronicle:test_finish_task()
    mock_vim.buffer = {
        "2024-01-01",
        "",
        "[ ] 12:33/ program @chronicle"
    }
    set_cursor(3)

    chronicle.finish()
    luaunit.assertEquals(
        "[x] 12:33/12:34 program @chronicle",
        get_current_line()
    )
end

function TestChronicle:test_finish_recurring_task()
    mock_vim.buffer = {
        "2024-01-01",
        "",
        "[ ] 12:33/ program @chronicle !every_day",
    }
    set_cursor(3)

    chronicle.finish()

    compare(
        {
            "2024-01-01",
            "",
            "[x] 12:33/12:34 program @chronicle !every_day",
            "",
            "2024-01-02",
            "",
            "[ ]             program @chronicle !every_day",
        },
        mock_vim.buffer
    )
end

function TestChronicle:test_finish_recurring_task_with_future_date()
    mock_vim.buffer = {
        "2024-01-01",
        "",
        "[ ] 12:33/ program @chronicle !every_day",
        "",
        "2024-01-03",
    }
    set_cursor(3)

    chronicle.finish()

    compare(
        {
            "2024-01-01",
            "",
            "[x] 12:33/12:34 program @chronicle !every_day",
            "",
            "2024-01-02",
            "",
            "[ ]             program @chronicle !every_day",
            "",
            "2024-01-03",
        },
        mock_vim.buffer
    )
end

-- Run the tests
luaunit.LuaUnit.verbosity = 2  -- Add verbosity for better output
os.exit(luaunit.LuaUnit.run()) 