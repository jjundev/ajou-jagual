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


# ch03-q01
C_CODE=''
C_TEST=''
assert 10*20*4==800
RESULTS['ch03-q01']={"method":'python',"result":"pass"}

# ch03-q04
C_CODE='#include <stdio.h>\n\nint main(void) {\n    int two[10];\n    two[0] = 1;\n    for (int i = 1; i < 10; ++i) two[i] = 2 * two[i - 1];\n    for (int i = 0; i < 10; ++i)\n        printf("%d%s", two[i], i == 9 ? "\\n" : " ");\n    return 0;\n}'
C_TEST=''
assert c_run(C_CODE)=="1 2 4 8 16 32 64 128 256 512\n"
RESULTS['ch03-q04']={"method":'c-run',"result":"pass"}

# ch03-q05
C_CODE='struct person {\n    char name[100];\n    int age;\n    float salary;\n};'
C_TEST='int main(void){struct person p={"Kim",20,1500.0f};assert(p.age==20);assert(p.salary==1500.0f);assert(strcmp(p.name,"Kim")==0);puts("OK");}'
assert c_run(C_CODE+"\n"+C_TEST)=="OK\n"
RESULTS['ch03-q05']={"method":'c-run',"result":"pass"}

# ch03-q06
C_CODE='typedef struct {\n    float real;\n    float imaginary;\n} complex;\ncomplex c1, c2;'
C_TEST='int main(void){c1.real=1.0f;c1.imaginary=2.0f;c2=c1;assert(c2.real==1.0f && c2.imaginary==2.0f);puts("OK");}'
assert c_run(C_CODE+"\n"+C_TEST)=="OK\n"
RESULTS['ch03-q06']={"method":'c-run',"result":"pass"}

print(json.dumps(RESULTS,ensure_ascii=False,sort_keys=True))
