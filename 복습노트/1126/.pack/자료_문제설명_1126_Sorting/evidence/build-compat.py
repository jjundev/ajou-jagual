"""Allow three static layouts from original exam tables, within the existing source-only allowlist."""
from pathlib import Path
import difflib
import importlib.util
import sys

repo = Path(sys.argv[1])
scripts = repo / ".agents/skills/ds-problem-explain/scripts"
path = scripts / "mpe_render.py"
sys.path.insert(0, str(scripts))
before = path.read_text(encoding="utf-8")
old = "                value == 'overflow-x:auto') or ("
new = """                value in ('overflow-x:auto', 'max-width:100%;overflow:auto')) or (
                node.tag == 'td' and value in ('white-space:nowrap;min-width:2.65rem',
                                              'white-space:nowrap;min-width:2ch')) or ("""
assert before.count(old) == 1
old_figure = "value in ('max-width:100%;overflow-x:auto',"
new_figure = "value in ('max-width:100%;overflow:auto', 'max-width:100%;overflow-x:auto',"
assert before.count(old_figure) == 1
after = before.replace(old, new, 1).replace(old_figure, new_figure, 1)
diff = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                   fromfile="official/mpe_render.py", tofile="scratch/mpe_render.py"))
(Path(__file__).resolve().parent / "source-table-compat.diff").write_text(diff, encoding="utf-8")
spec = importlib.util.spec_from_file_location("mpe_render",path)
renderer = importlib.util.module_from_spec(spec)
sys.modules["mpe_render"] = renderer
exec(compile(after, str(path), "exec"), renderer.__dict__)
from mpe_cli import main
raise SystemExit(main(sys.argv[2:]))

