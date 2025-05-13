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
    for i, line in ipairs(expected) do
        assert.are.equal(line, actual[i])
    end
end

describe("Chronicle", function()
    before_each(function()
        mock_vim.buffer = {}
    end)

    it("should start an event", function()

        mock_vim.buffer = {
            "2024-01-01",
            "",
            "program @chronicle"
        }
        set_cursor(3)

        chronicle.start()
        assert.are.equal(
            "    12:34/      program @chronicle", get_current_line()
        )
    end)

    it("should start a task", function()
        mock_vim.buffer = {
            "2024-01-01",
            "",
            "[ ] program @chronicle"
        }
        set_cursor(3)

        chronicle.start()
        assert.are.equal(
            "[ ] 12:34/      program @chronicle", get_current_line()
        )
    end)

    it("should finish an event", function()

        mock_vim.buffer = {
            "2024-01-01",
            "",
            "12:33/ program @chronicle"
        }
        set_cursor(3)

        chronicle.finish()
        assert.are.equal(
            "    12:33/12:34 program @chronicle", get_current_line()
        )
    end)

    it("should finish a task", function()
        mock_vim.buffer = {
            "2024-01-01",
            "",
            "[ ] 12:33/ program @chronicle"
        }
        set_cursor(3)

        chronicle.finish()
        assert.are.equal(
            "[x] 12:33/12:34 program @chronicle", get_current_line()
        )
    end)

    it("should finish a recurring task", function()
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
    end)
end) 