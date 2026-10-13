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


# ch03-q03
C_CODE=''
C_TEST='int main(void){int a[10];double b[10];char c[40];float d[10];printf("%zu %zu %zu %zu\\n",sizeof a,sizeof b,sizeof c,sizeof d);}'
assert c_run(C_TEST)=="40 80 40 40\n"
RESULTS['ch03-q03']={"method":'c-run',"result":"pass"}

# ch03-q07
C_CODE='typedef struct { float real, imag; } Complex;\nComplex complex_add(Complex a, Complex b) {\n    Complex result;\n    result.real = a.real + b.real;\n    result.imag = a.imag + b.imag;\n    return result;\n}'
C_TEST='int main(void){Complex a={1,2},b={3,4};Complex r=complex_add(a,b);assert(r.real==4 && r.imag==6);a.real=-5;r=complex_add(a,b);assert(r.real==-2 && r.imag==6);puts("OK");}'
assert c_run(C_CODE+"\n"+C_TEST)=="OK\n"
RESULTS['ch03-q07']={"method":'c-run',"result":"pass"}

# ch03-q12
C_CODE='#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\ntypedef struct { int value; char text[21]; } Record;\nint main(void) {\n    Record *p = malloc(sizeof *p);\n    if (p == NULL) return 1;\n    p->value = 100;\n    strcpy(p->text, "just testing");\n    printf("%d %s\\n", p->value, p->text);\n    free(p);\n    p = NULL;\n    return 0;\n}'
C_TEST=''
assert c_run(C_CODE)=="100 just testing\n"
RESULTS['ch03-q12']={"method":'c-run',"result":"pass"}

# ch01-q17
C_CODE=''
C_TEST=''
for n in [1,2,10,100]:
 a=list(range(n));comparisons=0;minimum=a[0];visits=0;total=0
 for x in a[1:]:comparisons+=1;minimum=min(minimum,x)
 for x in a:visits+=1;total+=x
 assert comparisons==n-1 and visits==n and total==n*(n-1)//2
RESULTS['ch01-q17']={"method":'python',"result":"pass"}

print(json.dumps(RESULTS,ensure_ascii=False,sort_keys=True))
