import hashlib,json
from pathlib import Path
import pytest
from _util import REPO
from explanation_delivery_checks import check_pack,check_preserved,latest_delivery_report
from pack_layout import current_path,current_digest

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

def test_republished_in_pack_layout_accepted(delivery):
 # A later publish writes manifest keys under .pack/; the report still names the pre-.pack paths.
 r,i,m,v=delivery;d=r/'복습노트/1012';pack=d/'.pack';pack.mkdir()
 (d/'문제설명_1012_Queue.md').rename(pack/'문제설명_1012_Queue.md');(d/'자료_문제설명_1012_Queue').rename(pack/'자료_문제설명_1012_Queue')
 manifest=pack/'자료_문제설명_1012_Queue/manifest.json'
 m['files']={'문제설명_1012_Queue.html':digest(d/'문제설명_1012_Queue.html'),'.pack/문제설명_1012_Queue.md':digest(pack/'문제설명_1012_Queue.md')}
 manifest.write_text(json.dumps(m));v['artifact_hashes']={**m['files'],'.pack/자료_문제설명_1012_Queue/manifest.json':digest(manifest)}
 (pack/'자료_문제설명_1012_Queue/validation.json').write_text(json.dumps(v))
 assert check_pack(r,i)==[]
 v['artifact_hashes']['.pack/문제설명_1012_Queue.md']='0'*64;(pack/'자료_문제설명_1012_Queue/validation.json').write_text(json.dumps(v))
 assert 'artifact hash set differs' in check_pack(r,i)

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
 # This immutable predecessor is the one bound by main's code-block replacement chain.
 report=REPO/'docs/verify/2026-10-12-ds-review-pack-explain.json';assert report.exists()
 packs=json.loads(report.read_text())['packs'];assert sorted(p['date'] for p in packs)==['0907','0914','0917','0921','0928','1001','1005','1008','1012']
 assert sum(len(p['problem_ids']) for p in packs)==64
 latest=json.loads((REPO/'docs/verify/2026-10-13-ds-code-blocks.json').read_text())
 assert digest(report)==latest['historical_report_sha256']
 by_date={p['date']:p for p in latest['packs']}
 for item in packs:
  current=by_date[item['date']]
  assert item['source']==current['source'] and item['source_sha256']==current['source_sha256']
  assert item['problem_ids']==current['problem_ids']
  assert check_pack(REPO,current)==[],item['date']
  # Predecessor artifact metadata is retained and connected to the current output.
  backup=current_path(REPO/current['replacements'][item['manifest']]['backup_file'])
  old=json.loads(backup.read_text())
  for name,old_digest in old['files'].items():
   relative=(Path(item['source']).parent/name).as_posix()
   assert check_preserved(REPO,relative,old_digest,latest)==[],relative


def test_forged_backup_digest_does_not_replace_backup_bytes(delivery):
 r,i,m,v=delivery;old=hashlib.sha256(b'old').hexdigest();replacement(r,i,i['html'],old)
 (Path(i['backup'])/('0-'+Path(i['html']).name)).write_bytes(b'not old')
 assert check_preserved(r,i['html'],old,{'packs':[i]})

def test_summary_retry_render_code_characters_once():
 from html import unescape
 import re
 targets=[('0914','Recursion','p9','1<log n'),('1001','List','p1','i >= loc'),('1012','Queue','p6','s->stack'),('1012','Queue','p12','s->top')]
 for date,slug,pid,token in targets:
  file=REPO/'복습노트'/date/'.pack'/f'자료_문제설명_{date}_{slug}'/'fragments'/f'{pid}.html'
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


def test_all_code_block_deliveries_current():
 report_path = REPO / 'docs/verify/2026-10-13-ds-code-blocks.json'
 assert report_path.exists()
 report = json.loads(report_path.read_text())
 assert {p['html'] for p in report['packs']} == {p.relative_to(REPO).as_posix() for p in (REPO/'복습노트').glob('*/문제설명_*.html')}
 for item in report['packs']:
  assert check_pack(REPO, item) == [], item['date']
  for rel, old in item['before_files'].items():
   assert check_preserved(REPO, rel, old, report) == [], rel
 for rel, old in report['protected_files'].items():
  data=current_path(REPO/rel).read_bytes();old=current_digest(REPO/rel,old)
  if rel=='.gitattributes':
   # The PDF font license adds only this narrow rule; every predecessor byte remains.
   extension=b'# Preserve the official font license byte-for-byte.\n.agents/skills/ds-review-pack/assets/pdf/vendor/jetbrains-mono/OFL.txt -whitespace\n'
   if data.endswith(extension):data=data[:-len(extension)]
  assert hashlib.sha256(data).hexdigest()==old, rel


def test_source_relocation_requires_matching_relative_path_and_digest(delivery):
 r,i,m,v=delivery
 m['source']='/previous/checkout/'+i['source']
 path=r/i['manifest'];path.write_text(json.dumps(m));v['artifact_hashes'][path.relative_to((r/i['source']).parent).as_posix()]=digest(path);(r/i['validation']).write_text(json.dumps(v))
 assert check_pack(r,i)==[]
 m['source']='/previous/checkout/another.html';path.write_text(json.dumps(m))
 assert check_pack(r,i)


def test_durable_backup_requires_real_bytes(delivery):
 r,i,m,v=delivery;rel=i['html'];old=hashlib.sha256(b'old').hexdigest()
 saved=r/'saved/0-previous.html';saved.parent.mkdir();saved.write_bytes(b'old')
 i['replacements'][rel]={'before_sha256':old,'after_sha256':digest(r/rel),'backup_sha256':old,'backup_file':saved.relative_to(r).as_posix()}
 assert check_preserved(r,rel,old,{'packs':[i]})==[]
 saved.write_bytes(b'forged');assert check_preserved(r,rel,old,{'packs':[i]})


def test_history_chain_requires_every_saved_predecessor(delivery):
 r,i,m,v=delivery;rel=i['html'];old=hashlib.sha256(b'old').hexdigest();middle=hashlib.sha256(b'middle').hexdigest()
 for name,data in [('old',b'old'),('middle',b'middle')]:
  (r/name).write_bytes(data)
 i['replacement_history']={rel:[{'before_sha256':old,'after_sha256':middle,'backup_sha256':old,'backup_file':'old'}]}
 i['replacements'][rel]={'before_sha256':middle,'after_sha256':digest(r/rel),'backup_sha256':middle,'backup_file':'middle'}
 assert check_preserved(r,rel,old,{'packs':[i]})==[]
 (r/'middle').unlink();assert check_preserved(r,rel,old,{'packs':[i]})


def test_replay_uses_published_inputs_without_original_run(tmp_path):
 import subprocess,sys
 runner=REPO/'docs/verify/rerun-ds-code-blocks.py'
 assert runner.is_file()
 result=subprocess.run([sys.executable,str(runner),'--repo',str(REPO),'--kind','independent','--output',str(tmp_path/'replay')],text=True,capture_output=True)
 assert result.returncode==0,result.stdout+result.stderr
 summary=json.loads((tmp_path/'replay/summary.json').read_text())
 assert summary['question_count']==64
 assert summary['pack_count']==9
 assert summary['input_location']=='published sources and fragments'


def test_saved_verification_rejects_zero_question_inputs(tmp_path):
 import subprocess,sys,shutil
 source=REPO/'복습노트/0907/.pack/자료_문제설명_0907_Intro_DS_Algorithms/evidence/verify-code-blocks.py'
 copied=tmp_path/'verify-code-blocks.py';shutil.copy2(source,copied)
 result=subprocess.run([sys.executable,str(copied)],text=True,capture_output=True)
 assert result.returncode!=0
 assert 'zero question inputs' in result.stdout+result.stderr


def test_replay_rejects_empty_published_question_set(tmp_path):
 import subprocess,sys
 report=tmp_path/'repo/docs/verify/2026-10-13-ds-code-blocks.json'
 report.parent.mkdir(parents=True);report.write_text(json.dumps({'packs':[]}))
 result=subprocess.run([sys.executable,str(REPO/'docs/verify/rerun-ds-code-blocks.py'),'--repo',str(tmp_path/'repo'),'--kind','independent','--output',str(tmp_path/'output')],text=True,capture_output=True)
 assert result.returncode!=0
 assert 'zero question inputs' in result.stdout+result.stderr
 assert not (tmp_path/'output/summary.json').exists()
