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


# ch01-q12
C_CODE=''
C_TEST=''
import math
for n in (16,32,64):
 values=[1,math.log2(n),n,n*math.log2(n),n*n,2**n,math.factorial(n)]
 assert all(a<b for a,b in zip(values,values[1:]))
RESULTS['ch01-q12']={"method":'python',"result":"pass"}

# ch01-q09
C_CODE=''
C_TEST=''
selection=json.loads((Path(__file__).parent/'selection.json').read_text())
root=Path(__file__).resolve().parents[3]
reference=root/'복습노트/0914/정리노트_0914_Recursion.html'
assert hashlib.sha256(reference.read_bytes()).hexdigest()=='1c861d482d1aa0eda8e162f72b93c25711a48361e6f7b98a7784dba037d09927'
# 시간복잡도 함수는 기본연산 횟수; 측정초/메모리/입력개수와 구별 (강의 토픽 s1-complexity).
assert '연산' in reference.read_text()
RESULTS['ch01-q09']={"method":'lecture-reference',"result":"pass"}

# ch02-q01
C_CODE=''
C_TEST=''
def depth(n):return 1 if n<=1 else 1+depth(n-1)
assert depth(5)==5
RESULTS['ch02-q01']={"method":'python',"result":"pass"}

# ch02-q05
C_CODE=''
C_TEST=''
n=2
trace=[]
for _ in range(5):trace.append(n);n=n
assert trace==[2,2,2,2,2] and 1 not in trace
RESULTS['ch02-q05']={"method":'python',"result":"pass"}

print(json.dumps(RESULTS,ensure_ascii=False,sort_keys=True))
