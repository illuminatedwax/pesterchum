module(..., package.seeall)
commands = {}

local function upper(text)
    return string.upper(text)
end
commands.luaupper = upper

local function lower(text)
    return string.lower(text)
end
commands.lualower = lower

local function utf8reverse(text)
    return text:gsub("([\194-\244][\128-\191]+)", string.reverse):reverse()
end
commands.luareverse = utf8reverse

