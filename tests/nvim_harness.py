import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from deepwick_spec.palette import load_palette

REPO = Path(__file__).resolve().parents[1]
PALETTE = load_palette()

requires_nvim = pytest.mark.skipif(shutil.which("nvim") is None, reason="requires nvim")

DUMP_LUA = r"""
local names = vim.json.decode(vim.env.DEEPWICK_GROUPS)
local function hex(v)
  if v == nil then return vim.NIL end
  return string.format("#%06x", v)
end
local out = { colors_name = vim.g.colors_name or vim.NIL, background = vim.o.background, groups = {}, terminal = {} }
for _, name in ipairs(names) do
  local hl = vim.api.nvim_get_hl(0, { name = name, link = false })
  out.groups[name] = {
    fg = hex(hl.fg), bg = hex(hl.bg), sp = hex(hl.sp),
    bold = hl.bold or false, italic = hl.italic or false, underline = hl.underline or false,
    undercurl = hl.undercurl or false, strikethrough = hl.strikethrough or false,
  }
end
for i = 0, 15 do out.terminal[i + 1] = vim.g["terminal_color_" .. i] or vim.NIL end
out.palette = require("deepwick.palette")
local ok, lualine = pcall(require, "lualine.themes.deepwick")
out.lualine = ok and lualine or vim.NIL
io.stdout:write(vim.json.encode(out))
"""


def hexof(name: str) -> str:
    return PALETTE.colors[name].lower()


def run_nvim(args: list[str], env_extra: dict | None = None) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:
        env = {
            **os.environ,
            "XDG_CONFIG_HOME": f"{tmp}/config",
            "XDG_DATA_HOME": f"{tmp}/data",
            "XDG_STATE_HOME": f"{tmp}/state",
            "XDG_CACHE_HOME": f"{tmp}/cache",
            **(env_extra or {}),
        }
        return subprocess.run(
            ["nvim", "--headless", "-u", "NONE", "-i", "NONE", "-n", "--cmd", f"set rtp^={REPO}", *args],
            capture_output=True, text=True, env=env, timeout=60,
        )


def nvim_dump(groups, before=(), apply=True) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "dump.lua"
        script.write_text(DUMP_LUA, encoding="utf-8")
        args = []
        for command in before:
            args += ["-c", command]
        if apply:
            args += ["-c", "colorscheme deepwick"]
        args += ["-c", f"luafile {script}", "-c", "qa!"]
        result = run_nvim(args, {"DEEPWICK_GROUPS": json.dumps(list(groups))})
    assert result.returncode == 0, result.stderr
    assert result.stderr == "", result.stderr
    return json.loads(result.stdout)


TS_SITE = Path(os.environ.get("DEEPWICK_TS_SITE", Path.home() / ".local/share/nvim/site"))
NVIM_TREESITTER = TS_SITE / "pack/core/opt/nvim-treesitter/runtime"
requires_python_parser = pytest.mark.skipif(
    not ((TS_SITE / "parser/python.so").is_file() and (NVIM_TREESITTER / "queries/python/highlights.scm").is_file()),
    reason="requires the Tree-sitter python parser and nvim-treesitter queries",
)

CAPTURE_LUA = r"""
local probe = vim.json.decode(vim.env.DEEPWICK_PROBE)
vim.cmd.edit(probe.file)
vim.treesitter.start(0, probe.lang)
vim.treesitter.get_parser(0):parse(true)
local out = {}
for _, pos in ipairs(probe.positions) do
  local caps = vim.inspect_pos(0, pos[1], pos[2], { syntax = false, extmarks = false, semantic_tokens = false }).treesitter
  local top = caps[#caps]
  local hl = vim.api.nvim_get_hl(0, { name = top.hl_group, link = false })
  out[#out + 1] = { capture = top.capture, fg = hl.fg and string.format("#%06x", hl.fg) or vim.NIL, bold = hl.bold or false }
end
io.stdout:write(vim.json.encode(out))
"""


def nvim_captures(path, lang, positions) -> list[dict]:
    """Top Tree-sitter capture and its resolved style at each 0-based (row, col)."""
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "captures.lua"
        script.write_text(CAPTURE_LUA, encoding="utf-8")
        probe = {"file": str(path), "lang": lang, "positions": positions}
        result = run_nvim(
            ["--cmd", f"set rtp^={TS_SITE}", "--cmd", f"set rtp^={NVIM_TREESITTER}",
             "-c", "colorscheme deepwick", "-c", f"luafile {script}", "-c", "qa!"],
            {"DEEPWICK_PROBE": json.dumps(probe)},
        )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)
