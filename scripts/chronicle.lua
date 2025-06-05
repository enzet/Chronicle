-- Script for Neovim to manage tasks in Chronicle project files.
-- See https://github.com/enzet/Chronicle for more information.

-- Reload it with `:source <path to Chronicle>/scripts/chronicle.lua`.

local M = {}

-- Validate date string format.
local function is_valid_date(date_str)
    if not date_str then return false end
    local year, month, day = date_str:match("^(%d%d%d%d)-(%d%d)-(%d%d)$")
    if not (year and month and day) then return false end
    return os.time({
        year = tonumber(year), month = tonumber(month), day = tonumber(day)
    }) ~= nil
end

-- Block of mockable Vim functions.

-- Notify user with a message.
local function notify(message)
    vim.notify(message, vim.log.levels.WARN)
end

-- Replace line under cursor with new line.
function M.replace(line)
    local bufnr = vim.api.nvim_get_current_buf()
    vim.api.nvim_buf_set_lines(
        bufnr,
        vim.api.nvim_win_get_cursor(0)[1] - 1,
        vim.api.nvim_win_get_cursor(0)[1],
        false,
        { line }
    )
end

-- Insert line after line under cursor.
function M.insert(line)
    local bufnr = vim.api.nvim_get_current_buf()
    vim.api.nvim_buf_set_lines(
        bufnr,
        vim.api.nvim_win_get_cursor(0)[1],
        vim.api.nvim_win_get_cursor(0)[1],
        false,
        { line }
    )
end

-- Insert line at line number.
function M.insert_at(line, line_number)
    local bufnr = vim.api.nvim_get_current_buf()
    vim.api.nvim_buf_set_lines(
        bufnr, line_number, line_number, false, { line }
    )
end

-- Get all lines in the current buffer.
function M.get_all_lines()
    local bufnr = vim.api.nvim_get_current_buf()
    return vim.api.nvim_buf_get_lines(bufnr, 0, -1, false)
end

-- Get line under cursor.
function M.get_current_line()
    local bufnr = vim.api.nvim_get_current_buf()
    return vim.api.nvim_buf_get_lines(
        bufnr,
        vim.api.nvim_win_get_cursor(0)[1] - 1,
        vim.api.nvim_win_get_cursor(0)[1],
        false
    )[1]
end

-- Get line number of cursor.
function M.get_cursor_line()
    return vim.api.nvim_win_get_cursor(0)[1]
end

function M.now()
    return os.date("%H:%M")
end

-- Parse line with event or task.
local function parse_event_line(line)

    -- Split line into parts by spaces.
    local parts = {}
    for part in line:gmatch("[^ ]+") do
        table.insert(parts, part)
    end

    local task_marker = nil
    local importance_marker = nil
    local start_time = nil
    local end_time = nil
    local repeat_tag = nil

    local in_content = false
    local content = ""

    for i, part in ipairs(parts) do

        if in_content then
            if part ~= "" then
                content = content .. " " .. part
            end
            if part:match("^!every_(.*)$") then
                repeat_tag = part:match("^!every_(.*)$")
            end
        elseif part == "[x]" then
            task_marker = part
        elseif part == "[" then
            task_marker = "[ ]"
        elseif part == "]" then
            -- Do nothing.
        elseif part == ">>>" then
            task_marker = ">>>"
        elseif part == "<!>" then
            importance_marker = "<!>"
        elseif part == "<.>" then
            importance_marker = "<.>"
        elseif part:match("^(%d%d:%d%d)/$") then
            start_time = part:match("^(%d%d:%d%d)/$")
        elseif part:match("^/(%d%d:%d%d)$") then
            end_time = part:match("^/(%d%d:%d%d)$")
        elseif part:match("^(%d%d:%d%d)/(%d%d:%d%d)$") then
            start_time = part:match("^(%d%d:%d%d)/")
            end_time = part:match("/(%d%d:%d%d)$")
        else
            in_content = true
            content = part
        end
    end

    return {
        task_marker = task_marker,
        importance_marker = importance_marker,
        start_time = start_time,
        end_time = end_time,
        repeat_tag = repeat_tag,
        content = content
    }
end

-- Convert event to line.
function event_to_line(event)
    local line = ""
    line = line .. (event.task_marker or "   ") .. " "
    line = line .. (event.start_time or "     ")
    line = line .. ((event.start_time or event.end_time) and "/" or " ")
    line = line .. (event.end_time or "     ")
    line = line .. " " .. (event.content or "")
    return line
end

-- Process line under cursor.
function M.process_line()
    local line = M.get_current_line()
    local lines = M.get_all_lines()
    local current_date = nil

    -- Search lines backwards from the current line until we find a date.
    for i = M.get_cursor_line(), 1, -1 do
        local current_line = lines[i]
        if is_valid_date(current_line) then
            current_date = current_line
            break
        end
    end

    if not current_date then
        notify("Chronicle: no valid date found above the current line")
        return
    end

    return {
        event = parse_event_line(line),
        current_date = current_date,
    }
end

-- Get next date.
local function get_next_date(current_date, interval)
    local year, month, day = current_date:match("(%d+)-(%d+)-(%d+)")
    local os_date = os.time({
        year = tonumber(year), month = tonumber(month), day = tonumber(day)
    })
    local new_date = os_date + interval * 86400
    return new_date
end

-- Get max day of month.
local function max_day_of_month(month)
    if month == 2 then
        return 28
    end
    if month == 4 or month == 6 or month == 9 or month == 11 then
        return 30
    end
    return 31
end

-- Get next month.
local function get_next_month(current_date)
    local year, month, day = current_date:match("(%d+)-(%d+)-(%d+)")
    local year_number = tonumber(year)
    local month_number = tonumber(month) + 1
    local day_number = tonumber(day)
    if month_number > 12 then
        month_number = 1
        year_number = year_number + 1
    end
    if day_number > max_day_of_month(month_number) then
        day_number = max_day_of_month(month_number)
    end
    local new_date = os.time({
        year = year_number, month = month_number, day = day_number
    })
    return new_date
end

-- Get next year.
local function get_next_year(current_date)
    local year, month, day = current_date:match("(%d+)-(%d+)-(%d+)")
    return os.time({
        year = tonumber(year) + 1, month = tonumber(month), day = tonumber(day)
    })
end

function M.repeat_task(event, current_date)

    local lines = M.get_all_lines()

    local new_task = ("[ ]             %s"):format(event.content)

    local next_date = nil
    if event.repeat_tag == "day" then
        next_date = get_next_date(current_date, 1)
    elseif event.repeat_tag:match("(%d+)_days") then
        next_date = get_next_date(
            current_date, tonumber(event.repeat_tag:match("(%d+)_days"))
        )
    elseif event.repeat_tag == "week" then
        next_date = get_next_date(current_date, 7)
    elseif event.repeat_tag == "month" then
        next_date = get_next_month(current_date)
    elseif event.repeat_tag == "year" then
        next_date = get_next_year(current_date)
    end

    if next_date == nil then
        notify("Chronicle: no valid repeat tag found")
        return
    end

    -- Search lines forwards for the next date.
    local found_line_number = nil
    for i = M.get_cursor_line(), #lines do
        local l = lines[i]
        if l:match("^%d%d%d%d%-%d%d%-%d%d$") then
            local year, month, day = l:match("(%d+)-(%d+)-(%d+)")
            local os_date = os.time({
                year = tonumber(year),
                month = tonumber(month),
                day = tonumber(day)
            })
            if os_date > next_date then
                -- Insert new lines with new date before `i`.
                M.insert_at(os.date("%Y-%m-%d", next_date), i - 1)
                i = i + 1
                M.insert_at("", i - 1)
                i = i + 1
                M.insert_at("", i - 1)
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
        M.insert_at("", #lines + 1)
        M.insert_at(os.date("%Y-%m-%d", next_date), #lines + 2)
        M.insert_at("", #lines + 3)
        found_line_number = #lines + 4
    end

    -- Insert new task.
    if found_line_number then
        M.insert_at(new_task, found_line_number - 1)
    end
end

-- Start event.
function M.start()
    local state = M.process_line()

    if not state.event then
        notify("Chronicle: no valid event found")
        return
    end

    -- Mark event as started now.
    state.event.start_time = M.now()

    M.replace(event_to_line(state.event))
end

-- Finish event. If it is a task, mark it as done.
function M.finish()
    local state = M.process_line()

    -- Mark event as finished now.
    if state.event.end_time == nil then
        state.event.end_time = M.now()
    end

    -- If event is a task, mark it as done.
    if state.event.task_marker == "[ ]" then
        state.event.task_marker = "[x]"
    end

    M.replace(event_to_line(state.event))

    -- If event is a repeat, create a new identical event.
    if state.event.repeat_tag then
        M.repeat_task(state.event, state.current_date)
    end
end

-- Finish event and create a new identical event.
function M.pause()
    local state = M.process_line()
    local is_task = state.event.task_marker == "[ ]"

    -- Mark event as finished now.
    state.event.end_time = M.now()

    -- If event is a task, make it a normal event.
    if is_task then
        state.event.task_marker = nil
    end

    -- Replace current line with new line.
    M.replace(event_to_line(state.event))

    -- Insert new line with new clean event.
    state.event.start_time = nil
    state.event.end_time = nil
    if is_task then
        state.event.task_marker = "[ ]"
    end
    M.insert(event_to_line(state.event))
end

local options = { noremap = true, silent = true }

-- If we are actually running in Neovim, not in tests.
if vim then
    vim.api.nvim_create_user_command("ChronicleDone", M.finish, {})
    vim.api.nvim_set_keymap("n", "<Space>d", ":ChronicleDone<CR>", options)

    vim.api.nvim_create_user_command("ChronicleStart", M.start, {})
    vim.api.nvim_set_keymap("n", "<Space>s", ":ChronicleStart<CR>", options)

    vim.api.nvim_create_user_command("ChroniclePause", M.pause, {})
    vim.api.nvim_set_keymap("n", "<Space>p", ":ChroniclePause<CR>", options)
end

return M
