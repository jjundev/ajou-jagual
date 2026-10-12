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


# ch02-q06
C_CODE=''
C_TEST=''
trace=list(range(5,-3,-1))
assert trace==[5,4,3,2,1,0,-1,-2]
RESULTS['ch02-q06']={"method":'python',"result":"pass"}

# ch02-q09
C_CODE=''
C_TEST='int recursive(int n){printf("%d\\n",n);if(n<1)return -1;return recursive(n-3)+1;}\nint main(void){printf("return=%d\\n",recursive(10));}'
assert c_run(C_TEST)=="10\n7\n4\n1\n-2\nreturn=3\n"
RESULTS['ch02-q09']={"method":'c-run',"result":"pass"}

# ch02-q13
C_CODE='int sum(int n) {\n    if (n <= 1) return 1;\n    return n + sum(n - 1);\n}'
C_TEST='int main(void){assert(sum(1)==1);assert(sum(4)==10);assert(sum(10)==55);puts("OK");}'
assert c_run(C_CODE+"\n"+C_TEST)=="OK\n"
RESULTS['ch02-q13']={"method":'c-run',"result":"pass"}

# ch02-q16
C_CODE='int sum_iter(int n) {\n    int total = 0;\n    for (int i = 1; i <= n; ++i) total += i;\n    return total;\n}'
C_TEST='int main(void){assert(sum_iter(1)==1);assert(sum_iter(5)==15);assert(sum_iter(10)==55);puts("OK");}'
assert c_run(C_CODE+"\n"+C_TEST)=="OK\n"
RESULTS['ch02-q16']={"method":'c-run',"result":"pass"}

print(json.dumps(RESULTS,ensure_ascii=False,sort_keys=True))
