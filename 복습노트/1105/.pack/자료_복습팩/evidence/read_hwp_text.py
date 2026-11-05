from pathlib import Path
import struct,zlib,json,re
r=Path(__file__).resolve().parents[1]
repo=r/'repo';bank=json.loads((repo/'from_the_past/기출/문제은행.json').read_text());src=next(x for x in bank['sources'] if x['id']=='2018-mid-c024');path=repo/'from_the_past/기출'/src['file'];raw=path.read_bytes()
assert raw[:8]==bytes.fromhex('D0CF11E0A1B11AE1')
ss=1<<struct.unpack_from('<H',raw,30)[0];ms=1<<struct.unpack_from('<H',raw,32)[0]
def sec(n):return raw[(n+1)*ss:(n+2)*ss]
fatids=[n for n in struct.unpack_from('<109I',raw,76) if n<0xFFFFFFFA]
fat=[]
for n in fatids:fat.extend(struct.unpack('<'+'I'*(ss//4),sec(n)))
def chain(n,table):
 seen=set()
 while n<0xFFFFFFFA:
  if n in seen:raise ValueError('cyclic sector chain')
  seen.add(n);yield n;n=table[n]
def readstream(n,size=None):return b''.join(sec(i) for i in chain(n,fat))[:size]
dirraw=readstream(struct.unpack_from('<I',raw,48)[0]);entries=[]
for i in range(0,len(dirraw),128):
 e=dirraw[i:i+128]
 if len(e)<128:continue
 nlen=struct.unpack_from('<H',e,64)[0]
 if nlen<2:continue
 entries.append(dict(name=e[:nlen-2].decode('utf16'),type=e[66],start=struct.unpack_from('<I',e,116)[0],size=struct.unpack_from('<Q',e,120)[0]))
root=next(e for e in entries if e['type']==5);mini=readstream(root['start'],root['size']);minifatraw=readstream(struct.unpack_from('<I',raw,60)[0]);minifat=struct.unpack('<'+'I'*(len(minifatraw)//4),minifatraw)
def entrydata(e):
 if e['size']<struct.unpack_from('<I',raw,56)[0]:return b''.join(mini[i*ms:(i+1)*ms] for i in chain(e['start'],minifat))[:e['size']]
 return readstream(e['start'],e['size'])
header=entrydata(next(e for e in entries if e['name']=='FileHeader'));compressed=struct.unpack_from('<I',header,36)[0]&1
texts=[]
for e in entries:
 if not re.fullmatch(r'Section\d+',e['name']):continue
 data=entrydata(e);data=zlib.decompress(data,-15) if compressed else data;offset=0
 while offset+4<=len(data):
  v=struct.unpack_from('<I',data,offset)[0];offset+=4;tag=v&1023;size=v>>20
  if size==4095:size=struct.unpack_from('<I',data,offset)[0];offset+=4
  body=data[offset:offset+size];offset+=size
  if tag==67:
   text=body.decode('utf-16le',errors='replace');texts.append(re.sub(r'[\x00-\x08\x0b-\x1f]',' ',text))
out=r/'work/2018-mid-c024-original-hwp-text.txt';out.write_text('\n'.join(texts));print(out)
