import copy
import hashlib
import fitz
from _util import SCRIPTS
from lecture_sources import validate_lecture_source

def test_lecture_reference_valid_and_bad_boundaries(tmp_path):
    pdf=tmp_path/'lecture.pdf'
    doc=fitz.open(); doc.new_page();doc.new_page();doc.save(pdf);doc.close()
    q={'source':'lecture-s02-p2-power','objectives':['power-trace'],'task_family':'power',
       'lecture_ref':{'path':'lecture.pdf','pdf_page':2,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'example':'power','taught_on':'0917'}}
    sessions=[{'date':'0917'}]
    assert validate_lecture_source(tmp_path,q,sessions)==[]
    assert validate_lecture_source(tmp_path,q,[{'date':'0917','slides':'S2 p1–1'}])
    for key,value in [('pdf_page',0),('pdf_page',3),('path','missing.pdf'),('path','../outside.pdf'),('sha256','0'*64),('taught_on','0921')]:
        bad=copy.deepcopy(q);bad['lecture_ref'][key]=value
        assert validate_lecture_source(tmp_path,bad,sessions),(key,value)

def test_missing_contract_rejected(tmp_path):
    assert validate_lecture_source(tmp_path,{},[])
