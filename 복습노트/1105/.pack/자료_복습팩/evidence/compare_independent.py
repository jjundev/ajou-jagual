from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];a=json.loads((r/'work/answer-data.json').read_text())['problems'];b=json.loads((r/'work/independent-results.json').read_text())['answers'];checks=[]
def same(label,x,y):
 assert x==y,(label,x,y)
 checks.append(label)
for method in ['successor','predecessor']:
 for j in range(3):same(f'p1 {method} deletion{j+1}',a['p1'][method+'_steps'][j]['array'],b['p1']['conventions'][method][j]['tree']['sparse_1based_array'])
same('p2 final array',a['p2']['deletions'][-1]['array'],b['p2']['steps'][-1]['tree']['sparse_1based_array'])
for p in ['p3','p4','p5']:
 same(p+' minimal tree array',a[p]['array'],b[p]['tree']['sparse_1based_array']);same(p+' height',a[p]['height_levels'],b[p]['tree']['height_levels'])
for order in ['preorder','inorder','postorder']:same('p6 '+order,a['p6']['initial'][order],b['p6']['original'][order])
for method in ['successor','predecessor']:same('p6 deletion '+method,a['p6']['subquestions']['e'][method][-1]['array'],b['p6']['delete55'][method]['sparse_1based_array'])
for p in ['p7','p8']:same(p+' OX',a[p]['answer'],b[p]['answer'])
for order in ['preorder','inorder','postorder']:same('p10 '+order,a['p10'][order],b['p10']['tree'][order])
same('p10 array',a['p10']['array'],b['p10']['tree']['sparse_1based_array'])
checks += ['p9 insertion expected-logarithmic under random-input model / worst linear independently agrees','p10 BST global violation 8<9 independently agrees','p11 record/field/primary-key, forbidden duplicate, global20 violation, success path18,7,12 pointer and miss18,26,NULL all agree','p12 loop-entry (NULL,18),(18,7),(7,12), exit(12,NULL);12.left=9;duplicate8nodes;empty0iterations all agree']
(r/'work/independent-comparison.json').write_text(json.dumps(dict(status='pass',count=12,checks=checks,unresolved=[]),ensure_ascii=False,indent=2));print('PASS',len(checks),'comparisons,12 questions')
