from pathlib import Path
import unicodedata as u,olefile,zlib,struct
r=Path.cwd();w=r/'tmp/ds-problem-explain/1012-20261012-first/review-1012-Queue/evidence'
p=next(p for p in (r/'from_the_past').rglob('*.hwp') if 'C024' in u.normalize('NFC',p.name))
o=olefile.OleFileIO(p);compressed=bool(struct.unpack_from('<I',o.openstream('FileHeader').read(),36)[0]&1);text=[]
for x in o.listdir():
 if x[0]=='BodyText':
  data=o.openstream(x).read();data=zlib.decompress(data,-15) if compressed else data;i=0
  while i+4<=len(data):
   h=struct.unpack_from('<I',data,i)[0];i+=4;tag=h&1023;size=h>>20
   if size==4095:size=struct.unpack_from('<I',data,i)[0];i+=4
   block=data[i:i+size];i+=size
   if tag==67:text.append(block.decode('utf-16le',errors='replace'))
(w/'2018-original.txt').write_text('\n'.join(text));print(p);print('\n'.join(text))
