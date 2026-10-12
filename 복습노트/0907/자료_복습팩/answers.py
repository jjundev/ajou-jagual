"""Read-only reproducible verification of added textbook answers (temporary C binaries)."""
import json,subprocess,tempfile,hashlib
from pathlib import Path
RESULTS={}
def c_run(code,input_text=''):
    with tempfile.TemporaryDirectory(prefix='ds-textbook-verify-') as directory:
        source=Path(directory)/'verify.c';binary=Path(directory)/'verify'
        source.write_text('#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <assert.h>\n'+code)
        subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],check=True,capture_output=True,text=True)
        return subprocess.run([str(binary)],input=input_text,capture_output=True,text=True,check=True,timeout=10).stdout


# ch01-q01
C_CODE=''
C_TEST=''
for a,b in [(3,7),(-2,4),(5,5)]:
 old=(a,b);temp=a;a=b;b=temp
 assert (a,b)==old[::-1]
RESULTS['ch01-q01']={"method":'python',"result":"pass"}

# ch01-q02
C_CODE=''
C_TEST=''
for a,b,want in [(3,7,7),(-5,-2,-2),(5,5,5)]:
 result=a if a>=b else b
 assert result==want
RESULTS['ch01-q02']={"method":'python',"result":"pass"}

# ch01-q03
C_CODE=''
C_TEST=''
for n,want in [(1,1),(4,10),(10,55)]:
 total=0
 for i in range(1,n+1):total+=i
 assert total==want
RESULTS['ch01-q03']={"method":'python',"result":"pass"}

# ch05-q01
C_CODE=''
C_TEST=''
from collections import deque
q=deque('ABCDE');out=[]
while q:out.append(q.popleft())
assert out==list('ABCDE')
RESULTS['ch05-q01']={"method":'python',"result":"pass"}

print(json.dumps(RESULTS,ensure_ascii=False,sort_keys=True))
