from pathlib import Path

from nvim_harness import hexof, nvim_captures, requires_nvim, requires_python_parser

SAMPLES = Path(__file__).resolve().parents[2] / "spec" / "samples"


def position(path, needle, word):
    lines = path.read_text(encoding="utf-8").splitlines()
    row = next(i for i, line in enumerate(lines) if needle in line)
    return [row, lines[row].index(needle) + needle.index(word)]


@requires_nvim
@requires_python_parser
def test_python_for_loop_in_is_control_flow_and_membership_in_is_not(tmp_path):
    member = tmp_path / "member.py"
    member.write_text("ok = x in y\n")
    loop = nvim_captures(SAMPLES / "sample.py", "python", [position(SAMPLES / "sample.py", "for name in names", "in ")])
    assert loop[0]["fg"] == hexof("magenta"), loop
    membership = nvim_captures(member, "python", [position(member, "x in y", "in ")])
    assert membership[0]["fg"] == hexof("foreground"), membership


@requires_nvim
@requires_python_parser
def test_python_import_keyword_renders_magenta():
    found = nvim_captures(SAMPLES / "sample.py", "python", [position(SAMPLES / "sample.py", "import re", "import")])
    assert found[0]["fg"] == hexof("magenta"), found
