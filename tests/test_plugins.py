import json
import shutil
import subprocess
from pathlib import Path

import pytest

from deepwick_spec.check_port import check_port
from nvim_harness import PALETTE, REPO, hexof, nvim_dump, requires_nvim, run_nvim

pytestmark = requires_nvim

AIRLINE = Path.home() / ".local/share/nvim/site/pack/core/opt/vim-airline"

PLUGIN_GROUPS = {
    "GitSignsAdd": ("green", None),
    "GitSignsChange": ("blue", None),
    "GitSignsDelete": ("red", None),
    "GitSignsAddInline": (None, "diffAddedEmph"),
    "GitSignsDeleteInline": (None, "diffRemovedEmph"),
    "GitSignsChangeInline": (None, "diffText"),
    "TelescopeNormal": ("foreground", "surface"),
    "TelescopeBorder": ("blue", "surface"),
    "TelescopeTitle": ("blue", "surface"),
    "TelescopeSelection": ("foreground", "selection"),
    "TelescopeMatching": ("blue", None),
    "TelescopePromptPrefix": ("blue", "surface"),
    "NvimTreeNormal": ("foreground", "background"),
    "NvimTreeWinSeparator": ("overlay", "background"),
    "NvimTreeRootFolder": ("blue", None),
    "NvimTreeFolderName": ("blue", None),
    "NvimTreeFolderIcon": ("blue", None),
    "NvimTreeIndentMarker": ("overlay", None),
    "NvimTreeSymlink": ("cyan", None),
    "NvimTreeExecFile": ("green", None),
    "NvimTreeGitDirtyIcon": ("blue", None),
    "NvimTreeGitStagedIcon": ("green", None),
    "NvimTreeGitNewIcon": ("teal", None),
    "NvimTreeGitDeletedIcon": ("red", None),
    "NvimTreeGitIgnoredIcon": ("muted", None),
    "NvimTreeCursorLine": (None, "surface"),
}


def test_plugin_groups():
    groups = nvim_dump(PLUGIN_GROUPS)["groups"]
    for name, (fg, bg) in PLUGIN_GROUPS.items():
        assert groups[name]["fg"] == (hexof(fg) if fg else None), f"{name} fg"
        assert groups[name]["bg"] == (hexof(bg) if bg else None), f"{name} bg"


def test_lualine_theme():
    theme = nvim_dump([])["lualine"]
    c = PALETTE.colors
    modes = {"normal": "blue", "insert": "green", "visual": "magenta", "replace": "red", "command": "yellow", "terminal": "teal"}
    for mode, color in modes.items():
        assert theme[mode]["a"] == {"fg": c["background"], "bg": c[color], "gui": "bold"}, mode
        assert theme[mode]["b"] == {"fg": c["foreground"], "bg": c["overlay"]}, mode
        assert theme[mode]["c"] == {"fg": c["foreground"], "bg": c["surface"]}, mode
    assert theme["inactive"]["c"] == {"fg": c["muted"], "bg": c["surface"]}


@pytest.mark.skipif(not AIRLINE.is_dir(), reason="requires vim-airline installed")
def test_airline_theme():
    result = run_nvim([
        "--cmd", f"set rtp+={AIRLINE}",
        "-c", "runtime autoload/airline/themes/deepwick.vim",
        "-c", "lua io.stdout:write(vim.json.encode(vim.g['airline#themes#deepwick#palette']))",
        "-c", "qa!",
    ])
    assert result.returncode == 0 and result.stderr == "", result.stderr
    theme = json.loads(result.stdout)
    c = PALETTE.colors
    modes = {"normal": "blue", "insert": "green", "visual": "magenta", "replace": "red", "commandline": "yellow"}
    for mode, color in modes.items():
        assert theme[mode]["airline_a"][:2] == [c["background"], c[color]], mode
        assert theme[mode]["airline_b"][:2] == [c["foreground"], c["overlay"]], mode
        assert theme[mode]["airline_c"][:2] == [c["foreground"], c["surface"]], mode
    assert theme["inactive"]["airline_c"][:2] == [c["muted"], c["surface"]]
    assert theme["accents"]["red"][0] == c["red"]


def test_airline_theme_guard():
    result = run_nvim(["-c", f"set rtp-={REPO}", "-c", f"source {REPO / 'autoload/airline/themes/deepwick.vim'}", "-c", "qa!"])
    assert "Deepwick airline theme needs Neovim with the deepwick port on 'runtimepath'" in result.stderr


def test_port_conventions():
    assert check_port(REPO, PALETTE.allowed_hex()) == []


@pytest.mark.skipif(shutil.which("vim") is None, reason="requires vim")
def test_airline_guard_message_survives_airlines_try(tmp_path):
    out = tmp_path / "messages.txt"
    subprocess.run(
        ["vim", "-es", "-N", "-u", "NONE", "-i", "NONE", "--cmd", f"set rtp^={REPO}",
         "-c", "try | runtime autoload/airline/themes/deepwick.vim | catch | endtry",
         "-c", f"redir! > {out} | silent messages | redir END", "-c", "qa!"],
        capture_output=True, text=True, timeout=30,
    )
    assert "Deepwick airline theme needs Neovim" in out.read_text()
