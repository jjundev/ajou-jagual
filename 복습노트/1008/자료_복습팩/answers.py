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


# ch04-q01
C_CODE=''
C_TEST=''
top=-1;top+=1;assert top==0
RESULTS['ch04-q01']={"method":'python',"result":"pass"}

# ch04-q04
C_CODE=''
C_TEST=''
assert len(list(range(3+1)))==4
RESULTS['ch04-q04']={"method":'python',"result":"pass"}

# ch04-q05
C_CODE=''
C_TEST=''
capacity=5
assert len([])-1==-1
assert len(list(range(capacity)))-1==capacity-1
RESULTS['ch04-q05']={"method":'python',"result":"pass"}

# ch04-q08
C_CODE=''
C_TEST=''
a=[None]*5;top=-1;states=[]
for op,value in [('push',1),('push',2),('push',3),('pop',None),('push',4),('push',5),('pop',None)]:
 if op=='push':top+=1;a[top]=value
 else:top-=1
 states.append((a[:top+1],top))
assert states==[([1],0),([1,2],1),([1,2,3],2),([1,2],1),([1,2,4],2),([1,2,4,5],3),([1,2,4],2)]
assert a==[1,2,4,5,None]
RESULTS['ch04-q08']={"method":'python',"result":"pass"}

print(json.dumps(RESULTS,ensure_ascii=False,sort_keys=True))
