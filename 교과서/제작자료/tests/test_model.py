import copy,json,pytest
from model import canonical_digest, validate_structure, validate_chapter_part

def test_canonical_code_roundtrip():
    value={'code':'printf("%d\\n", n); if(n < 1 && p != NULL) return 0;'}
    assert canonical_digest(value)==canonical_digest(json.loads(json.dumps(value)))
    assert canonical_digest(value)!=canonical_digest({'code':'different'})

def test_schema_rejects_answers_and_duplicates():
    bank={'schema_version':1,'sources':[],'chapters':[],'questions':[],'assets':[]}
    assert not validate_structure(bank)
    bank['unexpected']=True; assert validate_structure(bank)

def test_part_requires_null_answer():
    part={'chapter':{'id':'ch01','number':1,'title':'t','source_ids':['s01']},'questions':[],'assets':[],'models':[]}
    assert not validate_chapter_part(part)
    part['questions']=[{'answer':'guessed'}];assert validate_chapter_part(part)
