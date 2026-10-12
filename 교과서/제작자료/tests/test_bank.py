import json,shutil
from pathlib import Path
import pytest
from bank import bank_files,load_bank
from publish import package_fingerprint

@pytest.fixture
def chapter_copy(tmp_path):
    package=Path(__file__).parents[1].parent
    for path in bank_files(package):shutil.copy2(path,tmp_path/path.name)
    return tmp_path

@pytest.mark.parametrize('change',['filename','chapter','source','asset','duplicate'])
def test_rejects_misplaced_or_duplicate_chapter_data(chapter_copy,change):
    paths=bank_files(chapter_copy);path=paths[0];part=json.loads(path.read_text())
    if change=='filename':path.rename(chapter_copy/'99_wrong_연습문제.json')
    else:
        if change=='chapter':part['questions'][0]['chapter_id']='ch02'
        elif change=='source':part['questions'][0]['source_refs'][0]['source_id']='s02'
        elif change=='asset':part['questions'][0]['content']=[{'type':'figure','asset_id':'missing'}]
        else:part['questions'].append(part['questions'][0])
        path.write_text(json.dumps(part))
    with pytest.raises(ValueError):load_bank(chapter_copy)

def test_chapter_byte_change_invalidates_fingerprint(chapter_copy):
    package=Path(__file__).parents[1].parent
    (chapter_copy/'제작자료').mkdir();(chapter_copy/'assets').mkdir()
    for name in ('inventory.json','asset-models.json','preview.html'):
        shutil.copy2(package/'제작자료'/name,chapter_copy/'제작자료'/name)
    before=package_fingerprint(chapter_copy)
    path=bank_files(chapter_copy)[0];path.write_text(path.read_text()+'\n')
    assert package_fingerprint(chapter_copy)!=before
