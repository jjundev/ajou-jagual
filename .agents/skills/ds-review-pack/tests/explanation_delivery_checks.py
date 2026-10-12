"""Read-only delivery checks; historical records remain immutable."""
import hashlib,json
from pathlib import Path
from update_review import extract_cards

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def safe(root,name):
 p=(root/name).resolve()
 if not p.is_relative_to(root.resolve()):raise ValueError('path outside repository')
 return p

def check_pack(root,item):
 errors=[]
 try:
  if item['status']!='published':return ['delivery not published']
  src=safe(root,item['source']);digest=sha(src);cards=extract_cards(src.read_text());ids=[c['id'] for c in cards]
  manifest=safe(root,item['manifest']);m=json.loads(manifest.read_text());v=json.loads(safe(root,item['validation']).read_text());dest=src.parent
  if not ids or ids!=item['problem_ids'] or ids!=[p['id'] for p in m['problems']]:errors.append('current problem IDs differ')
  source_identity = Path(m['source']).resolve()==src
  if not source_identity and m.get('repo'):
   try: source_identity=Path(m['source']).relative_to(Path(m['repo'])).as_posix()==item['source']
   except ValueError: pass
  if digest!=item['source_sha256'] or digest!=m['source_sha256'] or not source_identity:errors.append('current source differs')
  if v.get('input_hash')!=m.get('input_hash'):errors.append('review input differs')
  expected={f"{p['id']}:{s}" for p in m['problems'] for s in p['subparts']}
  def approved(e):return isinstance(e,dict) and e.get('status')=='pass' and all(isinstance(e.get(k),str) and e[k].strip() for k in ('reviewer','evidence'))
  for kind in ('source_visual','content','independent','browser'):
   entry=v.get(kind,{})
   if not approved(entry):errors.append('unapproved '+kind)
   if kind in ('content','independent'):
    items=entry.get('items',{})
    if set(items)!=expected or any(not approved(e) for e in items.values()):errors.append('unapproved items '+kind)
    if kind=='independent' and any(e.get('method') not in ('exact','symbolic','numerical','proof','qualitative') or not e.get('conclusion') for e in items.values()):errors.append('independent conclusions missing')
  files={**m['files'],manifest.relative_to(dest).as_posix():sha(manifest)}
  if files!=v.get('artifact_hashes'):errors.append('artifact hash set differs')
  for name,d in files.items():
   path=safe(dest,name)
   if not path.is_file() or sha(path)!=d:errors.append('changed artifact '+name)
  for key in ('html','md'):
   path=safe(root,item[key])
   if path.parent!=dest or path.name not in m['files']:errors.append('missing '+key)
  for name,d in item.get('protected_files',{}).items():
   path=safe(root,name)
   if not path.is_file() or sha(path)!=d:errors.append('protected file changed '+name)
 except (OSError,ValueError,KeyError,TypeError) as e:errors.append(str(e))
 return errors

def check_preserved(root,relative,digest,report):
 try:
  path=safe(root,relative)
  if path.is_file() and sha(path)==digest:return []
  for item in (report or {}).get('packs',[]):
   parent=Path(item['source']).parent;stem=f"문제설명_{item['date']}_{item['slug']}"
   rel=Path(relative)
   try:owned=rel.relative_to(parent)
   except ValueError:continue
   if owned.as_posix() not in (stem+'.html',stem+'.md') and (len(owned.parts)<2 or owned.parts[0] not in ('figures_'+stem,'자료_'+stem)):continue
   replacement=item.get('replacements',{}).get(relative,{})
   if replacement.get('before_sha256')!=digest or replacement.get('backup_sha256')!=digest or check_pack(root,item):continue
   backup=Path(item.get('backup') or '')
   if not backup.is_absolute() or not backup.is_dir():continue
   if not any(saved.is_file() and sha(saved)==digest for saved in backup.rglob('*-'+path.name)):continue
   after=replacement.get('after_sha256')
   if (after is None and not path.exists()) or (path.is_file() and sha(path)==after):return []
 except (OSError,ValueError,KeyError,TypeError):pass
 return ['preserved digest mismatch: '+relative]


def latest_delivery_report(root):
 reports=sorted((Path(root)/'docs/verify').glob('*-ds-review-pack-explain.json'))
 return reports[-1] if reports else Path(root)/'docs/verify/2026-10-12-ds-review-pack-explain.json'
