"""Run defined C11 examples with CC, then report bound independent question evidence."""
from pathlib import Path
import json,os,shlex,subprocess,tempfile
root=Path(__file__).resolve().parent
compiler=shlex.split(os.environ.get('CC','cc'))
with tempfile.TemporaryDirectory() as temp:
 binary=Path(temp)/('verify.exe' if os.name=='nt' else 'verify')
 subprocess.run(compiler+['-std=c11','-Wall','-Wextra','-Werror',str(root/'verification.c'),'-o',str(binary)],check=True)
 print(subprocess.check_output([str(binary)],text=True))
s=json.loads((root/'selection.json').read_text(encoding='utf-8'))
for q in s['selected']:
 assert q['verification']['result']=='pass'
 print(q['id'],q['source'],q['verification']['method'])
