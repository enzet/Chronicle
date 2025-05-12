-- Tests for Lua Neovim script for Chronicle.
-- Run with: `busted scripts/test_chronicle.lua`.

local busted = require("busted")
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
    table.insert(mock_vim.buffer, line_number + 1, line)
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

-- Helper to simulate cursor movement.
local function set_cursor(line, column)
    mock_vim.cursor = {line, column or 0}
end

-- Helper to get current line.
local function get_current_line()
    return mock_vim.buffer[mock_vim.cursor[1]]
end

describe("Chronicle", function()
    before_each(function()
        -- Reset mock buffer before each test.
        mock_vim.buffer = {
            "2024-01-01",
            "                program @chronicle"
        }
        set_cursor(2)  -- Position cursor at the task line.
    end)

    it("should start a task", function()

        local mock_time = "12:34"
        os.date = function() return mock_time end

        chronicle.start()
        assert.are.equal(
            "    12:34/      program @chronicle", get_current_line()
        )
    end)

    it("should finish a task", function()

        mock_vim.buffer[2] = "    12:34/      program @chronicle"
        set_cursor(2)

        local mock_time = "12:35"
        os.date = function() return mock_time end
        chronicle.finish()
        assert.are.equal(
            "    12:34/12:35 program @chronicle", get_current_line()
        )
    end)
end) 