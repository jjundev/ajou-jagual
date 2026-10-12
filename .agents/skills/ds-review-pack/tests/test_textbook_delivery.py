"""Real delivered selections: provenance, scope, verified answers and preserved cards."""
import hashlib,json,os,unittest
from pathlib import Path
from _util import REPO
from update_review import extract_cards
from explanation_delivery_checks import check_preserved
ROOT=Path(os.environ.get('DS_REVIEW_DELIVERY_ROOT',REPO));DATES=('0907','0914','0917','0921','0928','1001','1005','1008','1012')
class DeliveryTests(unittest.TestCase):
 def selections(self):
  out=[]
  for d in DATES:
   p=ROOT/'복습노트'/d/'자료_복습팩';self.assertTrue((p/'selection.json').exists(),f'missing selection {d}')
   out.append((d,json.loads((p/'selection.json').read_text()),json.loads((p/'manifest.json').read_text()),json.loads((p/'validation.json').read_text())))
  return out
 def test_counts_and_chronological_originals_not_reused(self):
  used=set()
  for d,s,m,v in self.selections():
   self.assertEqual(s['mode'],'retrofit');self.assertTrue(4<=len(s['selected'])<=8 or v['unresolved']);self.assertEqual(v['counts']['total'],v['counts']['existing']+v['counts']['added'])
   for q in s['selected']:self.assertNotIn(q['source'],used);used.add(q['source'])
 def test_answers_evidence_and_dependencies(self):
  for d,s,m,v in self.selections():
   ids={q['source'] for q in s['selected']}
   for q in s['selected']:
    self.assertTrue(q['answer']);self.assertEqual(q['verification']['result'],'pass');self.assertTrue(q['evidence']);self.assertTrue(set(q['prerequisites'])<=ids)
    for ev in q['evidence']:
     file=REPO/ev['path'];self.assertTrue(file.exists());self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),ev['sha256'])
 def test_manifest_card_ids_and_existing_raw_hashes(self):
  for d,s,m,v in self.selections():
   cards=extract_cards(next((ROOT/'복습노트'/d).glob('복습문제*.html')).read_text());byid={c['id']:c for c in cards}
   self.assertEqual([c['id'] for c in cards],[q['id'] for q in m['problems']])
   for q in s['selected']:self.assertEqual(byid[q['id']]['source'],q['source'])
   for q in v['preserved']['cards']:self.assertEqual(hashlib.sha256(byid[q['id']]['raw'].encode()).hexdigest(),q['sha256'])
 def test_preserved_note_figures_and_explanations(self):
  for d,s,m,v in self.selections():
   for file,digest in v['preserved']['files'].items():
    report_path=ROOT/'docs/verify/2026-10-13-ds-code-blocks.json'
    report=json.loads(report_path.read_text()) if report_path.exists() else None
    self.assertEqual(check_preserved(ROOT,file,digest,report),[],file)
 def test_selected_ids_have_current_provenance(self):
  questions={q['id']:q for p in (REPO/'교과서').glob('*.json') for q in json.loads(p.read_text()).get('questions',[])}
  for d,s,m,v in self.selections():
   for q in s['selected']:
    original=questions[q['original_id']];self.assertEqual(q['source'],'textbook-'+original['id']);self.assertIsNone(original['answer']);self.assertEqual(q['provenance']['payload_sha256'],original['review']['payload_sha256']);self.assertEqual(q['provenance']['source_refs'],original['source_refs'])

class DeliveryContentTests(DeliveryTests):
 def test_connection_names_actual_note_topic(self):
  import re
  from html import unescape
  for date,selection,manifest,validation in self.selections():
   cards={c['id']:c for c in extract_cards(next((ROOT/'복습노트'/date).glob('복습문제*.html')).read_text())}
   titles={t['id']:t['title'] for s in manifest['sections'] for t in s['topics']}
   byid={q['id']:q for q in manifest['problems']}
   for q in selection['selected']:
    connection=re.search(r'<li>(수업과의 연결:.*?)</li>',cards[q['id']]['raw'],re.S)[1]
    self.assertIn(titles[byid[q['id']]['anchor']],unescape(connection))
 def test_displayed_complete_c_program_compiles(self):
  import re,subprocess,tempfile
  from html import unescape
  complete={'ch03-q04','ch03-q12','ch06-q10'}
  for date,selection,manifest,validation in self.selections():
   cards={c['id']:c for c in extract_cards(next((ROOT/'복습노트'/date).glob('복습문제*.html')).read_text())}
   for q in selection['selected']:
    if q['original_id'] not in complete:continue
    solution=cards[q['id']]['raw'].split('<details class="solution">')[1]
    code=unescape(re.search(r'<pre><code[^>]*>(.*?)</code></pre>',solution,re.S)[1])
    result=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-x','c','-fsyntax-only','-'],input=code,text=True,capture_output=True)
    self.assertEqual(result.returncode,0,result.stderr)
 def test_corrected_scope_pages(self):
  expected={'ch05-q01':14,'ch01-q09':28,'ch03-q08':11,'ch03-q09':11,'ch03-q10':12,'ch03-q11':12,'ch06-q03':21,'ch06-q04':29,'ch06-q07':29,'ch06-q10':29,'ch04-q01':11,'ch04-q11':21}
  for date,selection,manifest,validation in self.selections():
   for q in selection['selected']:
    if q['original_id'] in expected:
     pdf=[e for e in q['evidence'] if e['path'].endswith('.pdf')][0]
     self.assertEqual(pdf['locator'],f"PDF page {expected[q['original_id']]}")
