local M = {}

M.modules = { "editor", "syntax", "treesitter", "lsp" }

function M.load()
  if vim.g.colors_name then
    vim.cmd("highlight clear")
  end
  if vim.fn.exists("syntax_on") == 1 then
    vim.cmd("syntax reset")
  end
  vim.o.termguicolors = true
  vim.o.background = "dark"
  vim.g.colors_name = "deepwick"

  local palette = require("deepwick.palette")
  for _, module in ipairs(M.modules) do
    for name, spec in pairs(require("deepwick.groups." .. module)(palette)) do
      vim.api.nvim_set_hl(0, name, spec)
    end
  end
  for i, color in ipairs(palette.ansi) do
    vim.g["terminal_color_" .. (i - 1)] = color
  end
end

return M
