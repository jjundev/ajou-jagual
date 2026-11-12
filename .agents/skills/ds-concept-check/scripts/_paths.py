"""스킬 공용 경로와 NFC 폴더 찾기."""
import unicodedata
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REPO = SKILL.parents[2]
DS_REVIEW_PACK = REPO / ".agents" / "skills" / "ds-review-pack"


def find_nfc(directory: Path, name: str) -> Path | None:
    """directory 의 자식 중 NFC 정규화 이름이 name 과 같은 것. macOS NFD 저장 대응."""
    want = unicodedata.normalize("NFC", name)
    directory = Path(directory)
    if not directory.is_dir():
        return None
    for child in directory.iterdir():
        if unicodedata.normalize("NFC", child.name) == want:
            return child
    return None
