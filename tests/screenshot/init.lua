-- Isolated profile for README screenshots. Borrows the user's installed plugins
-- read-only and installs missing Tree-sitter parsers into the isolated data dir.
local repo = vim.fn.fnamemodify(debug.getinfo(1, "S").source:sub(2), ":p:h:h:h")
local site = vim.env.DEEPWICK_PLUGIN_SITE or (vim.env.HOME .. "/.local/share/nvim/site/pack/core/opt")

vim.opt.rtp:prepend(repo)
for _, name in ipairs({ "nvim-treesitter", "vim-airline", "nvim-web-devicons", "nvim-tree.lua" }) do
  vim.opt.rtp:append(site .. "/" .. name)
end

vim.opt.number = true
vim.opt.cursorline = true
vim.opt.showmode = false
vim.g.airline_theme = "deepwick"
vim.g.loaded_netrw = 1
vim.g.loaded_netrwPlugin = 1

require("nvim-treesitter").install({ "python", "typescript", "c", "markdown" }):wait(300000)
vim.api.nvim_create_autocmd("FileType", {
  callback = function(ev)
    pcall(vim.treesitter.start, ev.buf)
  end,
})
require("nvim-tree").setup({ view = { width = 24 } })
vim.cmd.colorscheme("deepwick")
