-- Script for Neovim to manage tasks in Chronicle project files.
-- See https://github.com/enzet/Chronicle for more information.

-- Reload it with `:source ~/.config/nvim/lua/chronicle.lua`.

local M = {}

-- Validate date string format.
local function is_valid_date(date_str)
    if not date_str then return false end
    local year, month, day = date_str:match("^(%d%d%d%d)-(%d%d)-(%d%d)$")
    if not (year and month and day) then return false end
    return os.time({year = tonumber(year), month = tonumber(month), day = tonumber(day)}) ~= nil
end

-- Process line under cursor.
function M.process_line(command)
    -- Input validation.
    if type(command) ~= "string" or (command ~= "done" and command ~= "start") then
        vim.notify("Invalid command: " .. tostring(command), vim.log.levels.ERROR)
        return
    end

    local bufnr = vim.api.nvim_get_current_buf()
    local line = vim.api.nvim_buf_get_lines(
        bufnr,
        vim.api.nvim_win_get_cursor(0)[1] - 1,
        vim.api.nvim_win_get_cursor(0)[1],
        false
    )[1]
    local lines = vim.api.nvim_buf_get_lines(bufnr, 0, -1, false)
    local current_date = nil

    -- Search lines backwards from the current line until we find a date.
    for i = vim.api.nvim_win_get_cursor(0)[1], 1, -1 do
        local l = lines[i]
        if is_valid_date(l) then
            current_date = l
            break
        end
    end

    if not current_date then
        vim.notify("No valid date found above the current line", vim.log.levels.WARN)
        return
    end

    local function get_next_date(current_date, interval)
        if not is_valid_date(current_date) then
            vim.notify("Invalid date format", vim.log.levels.ERROR)
            return nil
        end
        local year, month, day = current_date:match("(%d+)-(%d+)-(%d+)")
        local os_date = os.time({
            year = tonumber(year), month = tonumber(month), day = tonumber(day)
        })
        local new_date = os_date + interval * 86400 -- Add interval days
        return new_date
    end

    -- Rewrite line under cursor.
    local function rewrite_line_under_cursor(text)
        vim.api.nvim_buf_set_lines(
            bufnr,
            vim.api.nvim_win_get_cursor(0)[1] - 1,
            vim.api.nvim_win_get_cursor(0)[1],
            false,
            { text }
        )
    end

    -- Insert line.
    local function insert_line(text, i)
        vim.api.nvim_buf_set_lines(bufnr, i, i, false, { text })
    end

    -- Enhanced pattern matching with better error handling.
    local marker, start_time, end_time, content = line:match("^(%[[ x]%]) (.....).(.....) (.*)$")
    if not (marker and start_time and end_time and content) then
        vim.notify("Invalid task format", vim.log.levels.WARN)
        return
    end

    -- Mark unfinished task as complete.
    if command == "done" and line:match("^%[ %]") then
        if end_time == "     " then
            end_time = os.date("%H:%M")
        end
        local completed_line = "[x] " .. start_time .. "/" .. end_time .. " " .. content

        rewrite_line_under_cursor(completed_line)
        local new_task = "[ ]             " .. content

        -- Check if task needs to be repeated in the future.

        local next_date = nil
        if line:match("!every_day") then
            next_date = get_next_date(current_date, 1)
        elseif line:match("!every_(%d+)_days") then
            next_date = get_next_date(current_date, tonumber(line:match("!every_(%d+)_days")))
        elseif line:match("!every_week") then
            next_date = get_next_date(current_date, 7)
        elseif line:match("!every_month") then
            next_date = get_next_date(current_date, 30)
        end

        if next_date ~= nil then

            -- Search lines forwards for the next date.
            local found_line_number = nil
            for i = vim.api.nvim_win_get_cursor(0)[1], #lines do
                local l = lines[i]
                if l:match("^%d%d%d%d%-%d%d%-%d%d$") then
                    local year, month, day = l:match("(%d+)-(%d+)-(%d+)")
                    local os_date = os.time({ year = tonumber(year), month = tonumber(month), day = tonumber(day) })
                    if os_date > next_date then
                        -- Insert new lines with new date before `i`.
                        insert_line(os.date("%Y-%m-%d", next_date), i - 1)
                        i = i + 1
                        insert_line("", i - 1)
                        i = i + 1
                        insert_line("", i - 1)
                        found_line_number = i
                        break
                    end
                    if os_date == next_date then
                        found_line_number = i + 2
                        break
                    end
                end
            end

            -- If line number not found, insert new line at the end.
            if found_line_number == nil then
                insert_line(os.date("%Y-%m-%d", next_date), #lines + 1)
                insert_line("", #lines + 2)
                found_line_number = #lines + 3
            end

            -- Insert new task.
            if found_line_number then
                insert_line(new_task, found_line_number - 1)
            end
        end
    end

    -- Start new task.
    if command == "start" then
        local new_task = "[ ] " .. os.date("%H:%M") .. "/      " .. content
        rewrite_line_under_cursor(new_task)
    end
end

function M.finish_task()
    M.process_line("done")
end

function M.start_task()
    M.process_line("start")
end

local options = { noremap = true, silent = true }

vim.api.nvim_create_user_command("ChronicleDone", M.finish_task, {})
vim.api.nvim_set_keymap("n", "<Space>d", ":ChronicleDone<CR>", options)

vim.api.nvim_create_user_command("ChronicleStart", M.start_task, {})
vim.api.nvim_set_keymap("n", "<Space>s", ":ChronicleStart<CR>", options)

return M
