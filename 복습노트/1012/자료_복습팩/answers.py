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


# ch05-q03
C_CODE=''
C_TEST=''
from collections import deque
q=deque([10,20,30,40,50]);out=[q.popleft() for _ in range(3)]
assert out==[10,20,30] and list(q)==[40,50]
RESULTS['ch05-q03']={"method":'python',"result":"pass"}

# ch04-q07
C_CODE=''
C_TEST=''
stack=[]
for token in ['A','B','E','+','D','*','-']:
 if token not in '+*-':stack.append(token)
 else:
  right=stack.pop();left=stack.pop();first=(left,token,right);break
assert first==('B','+','E')
RESULTS['ch04-q07']={"method":'python',"result":"pass"}

# ch04-q11
C_CODE='#include <stdio.h>\n\nvoid print_numbers(const char *expression) {\n    int stack[1024], top = -1, next = 0, first = 1;\n    for (int i = 0; expression[i] != \'\\0\'; ++i) {\n        int value;\n        if (expression[i] == \'(\') {\n            if (top == 1023) return;\n            value = ++next;\n            stack[++top] = value;\n        } else if (expression[i] == \')\') {\n            if (top == -1) return;\n            value = stack[top--];\n        } else continue;\n        printf("%s%d", first ? "" : " ", value);\n        first = 0;\n    }\n    printf("\\n");\n}'
C_TEST='int main(void){print_numbers("((())(()))");print_numbers("((((()");print_numbers("()()");}'
assert c_run(C_CODE+"\n"+C_TEST)=="1 2 3 3 2 4 5 5 4 1\n1 2 3 4 5 5\n1 1 2 2\n"
RESULTS['ch04-q11']={"method":'c-run',"result":"pass"}

# ch04-q14
C_CODE='typedef struct { int data[100]; int top; } StackType;\nint size(const StackType *s) {\n    return s->top + 1;\n}'
C_TEST='int main(void){StackType s={.top=-1};assert(size(&s)==0);s.top=0;assert(size(&s)==1);s.top=99;assert(size(&s)==100);puts("OK");}'
assert c_run(C_CODE+"\n"+C_TEST)=="OK\n"
RESULTS['ch04-q14']={"method":'c-run',"result":"pass"}

print(json.dumps(RESULTS,ensure_ascii=False,sort_keys=True))
