import sys
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SKILL = TESTS.parent
SCRIPTS = SKILL / "scripts"
FIXTURES = TESTS / "fixtures"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
