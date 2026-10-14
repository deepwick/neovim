import json
import re

import pytest

from deepwick_spec.palette import ANSI_KEYS
from nvim_harness import PALETTE, hexof, nvim_dump, requires_nvim

pytestmark = requires_nvim

ROLE_GROUPS = {
    "comment": ["Comment", "SpecialComment", "@comment", "@comment.documentation", "@string.documentation", "@lsp.type.comment"],
    "keyword": ["Keyword", "Statement", "StorageClass", "Boolean", "@keyword", "@keyword.function", "@keyword.type",
                "@keyword.modifier", "@type.builtin", "@boolean", "@constant.builtin", "@variable.builtin", "@lsp.type.keyword"],
    "controlFlow": ["Conditional", "Repeat", "Exception", "Include", "@keyword.conditional", "@keyword.repeat",
                    "@keyword.return", "@keyword.exception", "@keyword.import", "@keyword.operator", "@keyword.coroutine"],
    "operator": ["Operator", "Delimiter", "@operator", "@punctuation.delimiter", "@punctuation.bracket", "@lsp.type.operator"],
    "type": ["Type", "Typedef", "@type", "@type.definition", "@module", "@constructor", "@lsp.type.class",
             "@lsp.type.namespace", "@lsp.type.type"],
    "interface": ["Structure", "@lsp.type.interface", "@lsp.type.enum", "@lsp.type.struct", "@lsp.type.typeParameter"],
    "function": ["Function", "@function", "@function.call", "@function.method", "@function.method.call",
                 "@function.builtin", "@attribute", "@lsp.type.function", "@lsp.type.method", "@lsp.type.decorator"],
    "macro": ["Macro", "@function.macro", "@constant.macro", "@lsp.type.macro"],
    "variable": ["Identifier", "@variable", "@variable.parameter", "@variable.member", "@property", "@tag.attribute",
                 "@lsp.type.variable", "@lsp.type.parameter", "@lsp.type.property"],
    "constant": ["Constant", "@constant", "@lsp.type.enumMember", "@lsp.typemod.variable.readonly",
                 "@lsp.typemod.property.readonly"],
    "string": ["String", "Character", "@string", "@character", "@lsp.type.string"],
    "escape": ["Special", "SpecialChar", "@string.escape", "@character.special"],
    "regex": ["@string.regexp", "@lsp.type.regexp"],
    "number": ["Number", "Float", "@number", "@number.float", "@lsp.type.number"],
    "tag": ["Tag", "@tag", "@tag.builtin"],
    "tagBracket": ["@tag.delimiter"],
    "preprocessor": ["PreProc", "PreCondit"],
    "preprocessorKeyword": ["Define", "@keyword.directive", "@keyword.directive.define", "@keyword.import.c", "@keyword.import.cpp"],
    "label": ["Label", "@label"],
    "heading": ["Title", "@markup.heading"],
    "bold": ["@markup.strong"],
    "italic": ["@markup.italic"],
    "link": ["@markup.link", "@markup.link.label"],
    "inlineCode": ["@markup.raw", "@markup.raw.block"],
    "invalid": ["Error"],
    "deprecated": ["@lsp.mod.deprecated", "DiagnosticDeprecated"],
}

# group: (fg color name or None, bg color name or None, required attributes)
UI = {
    "Normal": ("foreground", "background", set()),
    "NormalFloat": ("foreground", "surface", set()),
    "FloatBorder": ("blue", "surface", set()),
    "Cursor": ("background", "foreground", set()),
    "CursorLine": (None, "surface", set()),
    "CursorLineNr": ("foreground", None, {"bold"}),
    "LineNr": ("muted", None, set()),
    "SignColumn": (None, "background", set()),
    "Folded": ("comment", "surface", set()),
    "WinSeparator": ("overlay", None, set()),
    "StatusLine": ("foreground", "surface", set()),
    "StatusLineNC": ("muted", "surface", set()),
    "TabLineSel": ("foreground", "background", {"bold"}),
    "Pmenu": ("foreground", "surface", set()),
    "PmenuSel": ("foreground", "selection", set()),
    "PmenuThumb": (None, "muted", set()),
    "Visual": (None, "selection", set()),
    "Search": (None, "selection", set()),
    "CurSearch": ("gold", "selection", {"bold"}),
    "IncSearch": ("gold", "selection", {"bold"}),
    "MatchParen": ("gold", None, {"bold"}),
    "NonText": ("muted", None, set()),
    "EndOfBuffer": ("background", None, set()),
    "Whitespace": ("overlay", None, set()),
    "Directory": ("blue", None, set()),
    "ErrorMsg": ("red", None, set()),
    "WarningMsg": ("yellow", None, set()),
    "MoreMsg": ("green", None, set()),
    "QuickFixLine": (None, "selection", set()),
    "DiffAdd": (None, "diffAdded", set()),
    "DiffChange": (None, "diffChanged", set()),
    "DiffDelete": ("red", "diffRemoved", set()),
    "DiffText": (None, "diffText", set()),
    "Added": ("green", None, set()),
    "Changed": ("blue", None, set()),
    "Removed": ("red", None, set()),
    "Todo": ("blue", None, {"bold"}),
    "@diff.plus": ("green", None, set()),
    "@diff.minus": ("red", None, set()),
    "@diff.delta": ("blue", None, set()),
    "DiagnosticError": ("red", None, set()),
    "DiagnosticWarn": ("yellow", None, set()),
    "DiagnosticInfo": ("cyan", None, set()),
    "DiagnosticHint": ("muted", None, set()),
    "DiagnosticOk": ("green", None, set()),
    "DiagnosticUnnecessary": ("muted", None, set()),
    "LspReferenceText": (None, "overlay", set()),
    "LspReferenceWrite": (None, "selection", set()),
    "LspInlayHint": ("muted", None, set()),
}

UNDERCURLS = {
    "SpellBad": "red", "SpellCap": "yellow", "SpellLocal": "cyan", "SpellRare": "magenta",
    "DiagnosticUnderlineError": "red", "DiagnosticUnderlineWarn": "yellow",
    "DiagnosticUnderlineInfo": "cyan", "DiagnosticUnderlineHint": "muted", "DiagnosticUnderlineOk": "green",
}


def check(hl, fg, bg, attrs, label):
    assert hl["fg"] == (hexof(fg) if fg else None), f"{label} fg"
    assert hl["bg"] == (hexof(bg) if bg else None), f"{label} bg"
    for attr in attrs:
        assert hl[attr], f"{label} {attr}"


def snake(name):
    return re.sub(r"([A-Z])", lambda m: "_" + m.group(1).lower(), name)


def test_loads_and_sets_name_and_dark_background():
    out = nvim_dump(["Normal"])
    assert out["colors_name"] == "deepwick"
    assert out["background"] == "dark"


def test_palette_lua_matches_palette_json():
    lua = nvim_dump([])["palette"]
    for name, hex_ in PALETTE.colors.items():
        assert lua[snake(name)] == hex_, name
    assert lua["ansi"] == [PALETTE.ansi[k] for k in ANSI_KEYS]


def test_terminal_colors_are_ansi_16():
    assert nvim_dump([])["terminal"] == [PALETTE.ansi[k] for k in ANSI_KEYS]


def test_every_spec_syntax_role_is_mapped():
    assert set(ROLE_GROUPS) == set(PALETTE.syntax)


@pytest.mark.parametrize("role", sorted(ROLE_GROUPS))
def test_syntax_role_groups(role):
    style = PALETTE.syntax[role]
    groups = nvim_dump(ROLE_GROUPS[role])["groups"]
    for name in ROLE_GROUPS[role]:
        check(groups[name], style.color, None, set(style.style), name)


def test_ui_groups():
    groups = nvim_dump(UI)["groups"]
    for name, (fg, bg, attrs) in UI.items():
        check(groups[name], fg, bg, attrs, name)


def test_undercurl_groups():
    groups = nvim_dump(UNDERCURLS)["groups"]
    for name, color in UNDERCURLS.items():
        assert groups[name]["undercurl"], name
        assert groups[name]["sp"] == hexof(color), name


def test_c_include_is_preprocessor_keyword():
    groups = nvim_dump(["@keyword.import", "@keyword.import.c", "@keyword.import.python"])["groups"]
    assert groups["@keyword.import"]["fg"] == hexof("magenta")
    assert groups["@keyword.import.python"]["fg"] in (hexof("magenta"), None)
    assert groups["@keyword.import.c"]["fg"] == hexof("foreground")


def test_reload_after_other_scheme():
    out = nvim_dump(["Normal", "Comment", "Visual"], before=["colorscheme habamax", "set background=light"])
    assert out["background"] == "dark"
    check(out["groups"]["Normal"], "foreground", "background", set(), "Normal")
    check(out["groups"]["Comment"], "comment", None, {"italic"}, "Comment")
    check(out["groups"]["Visual"], None, "selection", set(), "Visual")


def test_switching_schemes_leaves_no_leftover_groups():
    from nvim_harness import run_nvim

    dump = "lua io.stdout:write(vim.json.encode(vim.api.nvim_get_hl(0, {})))"
    fresh = run_nvim(["-c", "colorscheme deepwick", "-c", dump, "-c", "qa!"])
    switched = run_nvim(["-c", "colorscheme habamax", "-c", "set background=light", "-c", "colorscheme deepwick", "-c", dump, "-c", "qa!"])
    assert fresh.stderr == switched.stderr == ""
    before, after = json.loads(fresh.stdout), json.loads(switched.stdout)
    leaked = sorted(name for name in before if after.get(name) != before[name])
    assert leaked == []


def test_python_logical_keywords_are_operators():
    groups = nvim_dump(["@keyword.operator", "@keyword.operator.python"])["groups"]
    assert groups["@keyword.operator"]["fg"] == hexof("magenta")
    assert groups["@keyword.operator.python"]["fg"] == hexof("foreground")


def test_python_builtin_types_are_types():
    groups = nvim_dump(["@type.builtin", "@type.builtin.python"])["groups"]
    assert groups["@type.builtin"]["fg"] == hexof("blue")
    assert groups["@type.builtin.python"]["fg"] == hexof("teal")
