local c = require("deepwick.palette")

local function mode(color)
  return {
    a = { fg = c.background, bg = color, gui = "bold" },
    b = { fg = c.foreground, bg = c.overlay },
    c = { fg = c.foreground, bg = c.surface },
  }
end

local inactive = { fg = c.muted, bg = c.surface }

return {
  normal = mode(c.blue),
  insert = mode(c.green),
  visual = mode(c.magenta),
  replace = mode(c.red),
  command = mode(c.yellow),
  terminal = mode(c.teal),
  inactive = { a = inactive, b = inactive, c = inactive },
}
