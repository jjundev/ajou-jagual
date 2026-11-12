"""SKILL.md·작성 규칙·.claude 링크가 실제 스크립트와 맞는지."""
from concept_util import SKILL

REPO = SKILL.parents[2]


def test_skill_mentions_every_script():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for name in ("check.py", "build.py", "blind.py", "browser_check.py", "item-rules.md", "blind-brief.md"):
        assert name in text and any(SKILL.rglob(name))


def test_claude_link():
    link = REPO / ".claude/skills/ds-concept-check"
    assert link.is_symlink() and link.resolve() == SKILL.resolve()


def test_item_rules_lists_compute_ops():
    import tree
    rules = (SKILL / "references/item-rules.md").read_text(encoding="utf-8")
    for op in tree.OPS:
        assert f"`{op}`" in rules


def test_item_rules_lists_every_check_code():
    import re
    code = (SKILL / "scripts/check.py").read_text(encoding="utf-8")
    rules = (SKILL / "references/item-rules.md").read_text(encoding="utf-8")
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    codes = set(re.findall(r'add\("([a-z-]+)"', code))
    assert {"steps", "distance"} <= codes
    for c in codes:
        assert f"[{c}]" in rules, c
        assert f"`{c}`" in skill, c
