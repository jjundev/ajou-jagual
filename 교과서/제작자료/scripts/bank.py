"""Read chapter JSON files as one in-memory bank; preserve on-disk separation."""
from pathlib import Path
import json
from model import validate_structure

def bank_files(package):
    files=sorted(Path(package).glob('[0-9][0-9]_*_연습문제.json'))
    if not files:raise ValueError('no chapter JSON files')
    if any(p.is_symlink() for p in files):raise ValueError('chapter symlink')
    return files

def load_bank(package):
    result={'schema_version':1,'sources':[],'chapters':[],'questions':[],'assets':[]}
    seen={key:set() for key in ('sources','chapters','questions','assets')}
    for path in bank_files(package):
        part=json.loads(path.read_text())
        errors=validate_structure(part)
        if errors:raise ValueError(str(path)+': '+str(errors))
        if len(part['chapters'])!=1:raise ValueError('expected one chapter per file')
        chapter=part['chapters'][0]
        if path.name!=f"{chapter['number']:02d}_{chapter['title']}_연습문제.json":raise ValueError('chapter filename mismatch')
        source_ids=set(chapter['source_ids']);asset_ids={a['id'] for a in part['assets']}
        if {s['id'] for s in part['sources']}!=source_ids:raise ValueError('chapter source mismatch')
        if any(q['chapter_id']!=chapter['id'] for q in part['questions']):raise ValueError('question in wrong chapter')
        def check(node):
            if isinstance(node,dict):
                if 'source_id' in node and node['source_id'] not in source_ids:raise ValueError('cross-chapter source')
                if 'asset_id' in node and node['asset_id'] not in asset_ids:raise ValueError('cross-chapter asset')
                for value in node.values():check(value)
            elif isinstance(node,list):
                for value in node:check(value)
        check(part)
        for key in seen:
            for item in part[key]:
                if item['id'] in seen[key]:raise ValueError('duplicate '+key+' ID: '+item['id'])
                seen[key].add(item['id']);result[key].append(item)
    return result
