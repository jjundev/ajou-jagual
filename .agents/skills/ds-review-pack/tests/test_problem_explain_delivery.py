import hashlib,json
from pathlib import Path
import pytest
from _util import REPO
from explanation_delivery_checks import check_pack,check_preserved,latest_delivery_report

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
@pytest.fixture
def delivery(tmp_path):
 d=tmp_path/'복습노트/1012';d.mkdir(parents=True)
 src=d/'복습문제_1012_Queue.html';src.write_text(''.join(f'<article class="card" id="p{i}" data-source="test-{i}"><h3>Q{i}</h3><div class="problem">Question</div></article>' for i in range(1,13)))
 stem='문제설명_1012_Queue';html=d/(stem+'.html');md=d/(stem+'.md');html.write_text('new');md.write_text('new md')
 data=d/('자료_'+stem);data.mkdir();manifest=data/'manifest.json';validation=data/'validation.json'
 files={html.name:digest(html),md.name:digest(md)}
 m={'source':str(src),'source_sha256':digest(src),'problems':[{'id':f'p{i}','subparts':['main']} for i in range(1,13)],'files':files,'input_hash':'abc'}
 manifest.write_text(json.dumps(m));v={'input_hash':'abc','artifact_hashes':{**files,manifest.relative_to(d).as_posix():digest(manifest)}}
 for kind in ('source_visual','content','independent','browser'):
  v[kind]={'status':'pass','reviewer':'fixture','evidence':'fixture'}
  if kind in ('content','independent'):v[kind]['items']={f'p{i}:main':{'status':'pass','reviewer':'fixture','evidence':'fixture','method':'exact','conclusion':'fixture'} for i in range(1,13)}
 validation.write_text(json.dumps(v));item={'date':'1012','slug':'Queue','source':src.relative_to(tmp_path).as_posix(),'source_sha256':digest(src),'problem_ids':[f'p{i}' for i in range(1,13)],'status':'published','html':html.relative_to(tmp_path).as_posix(),'md':md.relative_to(tmp_path).as_posix(),'manifest':manifest.relative_to(tmp_path).as_posix(),'validation':validation.relative_to(tmp_path).as_posix(),'protected_files':{src.relative_to(tmp_path).as_posix():digest(src)},'replacements':{}}
 return tmp_path,item,m,v

def test_current_source_and_all_problem_ids_required(delivery):
 r,i,m,v=delivery;assert check_pack(r,i)==[]
 i['problem_ids']=i['problem_ids'][:8];assert check_pack(r,i)
 i['problem_ids']=[f'p{n}' for n in range(1,13)];i['source_sha256']='old';assert check_pack(r,i)
 m['problems']=m['problems'][:8];(r/i['manifest']).write_text(json.dumps(m));assert check_pack(r,i)

@pytest.mark.parametrize('status',['not_run','fail','disputed'])
def test_unreviewed_delivery_rejected(delivery,status):
 r,i,m,v=delivery;v['independent']['items']['p12:main']['status']=status;(r/i['validation']).write_text(json.dumps(v));assert check_pack(r,i)

def replacement(r,i,path,before,backup=True):
 backup_dir=r/'backups';backup_dir.mkdir(exist_ok=True);i['backup']=str(backup_dir)
 (backup_dir/('0-'+Path(path).name)).write_bytes(b'old')
 i['replacements'][path]={'before_sha256':before,'after_sha256':digest(r/path),'backup_sha256':before if backup else None}

def test_exact_explanation_ownership_only(delivery):
 r,i,m,v=delivery;old=hashlib.sha256(b'old').hexdigest()
 for name in ('정리노트_1012_Queue.html','자료_복습팩/validation.json'):
  p=r/'복습노트/1012'/name;p.parent.mkdir(exist_ok=True);p.write_text('new');rel=p.relative_to(r).as_posix();replacement(r,i,rel,old);assert check_preserved(r,rel,old,{'packs':[i]})

def test_unrecorded_or_unbacked_change_rejected(delivery):
 r,i,m,v=delivery;old=hashlib.sha256(b'old').hexdigest();rel=i['html'];assert check_preserved(r,rel,old,{'packs':[i]})
 replacement(r,i,rel,old,False);assert check_preserved(r,rel,old,{'packs':[i]})
 replacement(r,i,rel,'wrong');assert check_preserved(r,rel,old,{'packs':[i]})

def test_historical_record_survives_valid_replacement(delivery):
 r,i,m,v=delivery;old=hashlib.sha256(b'old').hexdigest();history=r/'historical.json';history.write_text(json.dumps({i['html']:old}));before=history.read_bytes();replacement(r,i,i['html'],old)
 assert check_preserved(r,i['html'],old,{'packs':[i]})==[];assert history.read_bytes()==before
 assert check_preserved(r,i['source'],i['source_sha256'],None)==[]

def test_real_delivery():
 report=latest_delivery_report(REPO);assert report.exists()
 packs=json.loads(report.read_text())['packs'];assert sorted(p['date'] for p in packs)==['0907','0914','0917','0921','0928','1001','1005','1008','1012']
 assert sum(len(p['problem_ids']) for p in packs)==64
 for item in packs:assert check_pack(REPO,item)==[],item['date']


def test_forged_backup_digest_does_not_replace_backup_bytes(delivery):
 r,i,m,v=delivery;old=hashlib.sha256(b'old').hexdigest();replacement(r,i,i['html'],old)
 (Path(i['backup'])/('0-'+Path(i['html']).name)).write_bytes(b'not old')
 assert check_preserved(r,i['html'],old,{'packs':[i]})

def test_summary_retry_render_code_characters_once():
 from html import unescape
 import re
 targets=[('0914','Recursion','p9','1<log n'),('1001','List','p1','i >= loc'),('1012','Queue','p6','s->stack'),('1012','Queue','p12','s->top')]
 for date,slug,pid,token in targets:
  file=REPO/'복습노트'/date/f'자료_문제설명_{date}_{slug}'/'fragments'/f'{pid}.html'
  fragment=file.read_text();retry=fragment.split('data-explanation="retry"')[1].split('<div class="sum"')[0]
  summary=fragment.split('<div class="sum"')[1]
  rendered=unescape(re.sub('<[^>]+>','',retry+summary))
  assert '&lt;' not in rendered and '&gt;' not in rendered,(date,pid,rendered)
  assert token in rendered,(date,pid)

def test_frozen_manifest_source_is_portable_with_repo_relative_identity(delivery):
 r,i,m,v=delivery
 m['repo']='/old/course-checkout';m['source']=str(Path(m['repo'])/i['source'])
 (r/i['manifest']).write_text(json.dumps(m))
 v['artifact_hashes'][i['manifest'].split('복습노트/1012/')[1]]=digest(r/i['manifest'])
 (r/i['validation']).write_text(json.dumps(v))
 assert check_pack(r,i)==[]

def test_latest_delivery_report_preferred(tmp_path):
 from explanation_delivery_checks import latest_delivery_report
 folder=tmp_path/'docs/verify';folder.mkdir(parents=True)
 old=folder/'2026-10-12-ds-review-pack-explain.json';new=folder/'2026-10-13-ds-review-pack-explain.json'
 old.write_text('{}');new.write_text('{}')
 assert latest_delivery_report(tmp_path)==new
