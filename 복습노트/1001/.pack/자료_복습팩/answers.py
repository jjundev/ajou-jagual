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


# ch03-q08
C_CODE='int items;\nvoid insert(int array[], int loc, int value) {\n    for (int i = items; i > loc; --i) array[i] = array[i - 1];\n    array[loc] = value;\n    ++items;\n}'
C_TEST='int main(void){int a[100]={10,20,30};items=3;insert(a,1,99);assert(items==4 && a[0]==10 && a[1]==99 && a[2]==20 && a[3]==30);insert(a,0,7);insert(a,items,8);assert(items==6 && a[0]==7 && a[5]==8);puts("OK");}'
assert c_run(C_CODE+"\n"+C_TEST)=="OK\n"
RESULTS['ch03-q08']={"method":'c-run',"result":"pass"}

# ch03-q09
C_CODE=''
C_TEST=''
for items in [1,3,20]:
 assert sum(1 for i in range(items,0,-1))==items
 assert len(range(items,items,-1))==0
RESULTS['ch03-q09']={"method":'python',"result":"pass"}

# ch03-q10
C_CODE='int items;\nint delete(int array[], int loc) {\n    int removed = array[loc];\n    for (int i = loc; i < items - 1; ++i) array[i] = array[i + 1];\n    --items;\n    return removed;\n}'
C_TEST='int main(void){int a[100]={10,20,30,40};items=4;assert(delete(a,1)==20);assert(items==3 && a[0]==10 && a[1]==30 && a[2]==40);assert(delete(a,2)==40);assert(delete(a,0)==10);assert(items==1 && a[0]==30);assert(delete(a,0)==30 && items==0);puts("OK");}'
assert c_run(C_CODE+"\n"+C_TEST)=="OK\n"
RESULTS['ch03-q10']={"method":'c-run',"result":"pass"}

# ch03-q11
C_CODE=''
C_TEST=''
for items in [1,3,20]:
 assert len(range(0,items-1))==items-1
 assert len(range(items-1,items-1))==0
RESULTS['ch03-q11']={"method":'python',"result":"pass"}

print(json.dumps(RESULTS,ensure_ascii=False,sort_keys=True))
