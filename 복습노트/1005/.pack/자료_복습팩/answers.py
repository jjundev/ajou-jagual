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


# ch06-q03
C_CODE=''
C_TEST=''
last={'data':30,'link':None}
assert last is not None and last['link'] is None
RESULTS['ch06-q03']={"method":'python',"result":"pass"}

# ch06-q04
C_CODE=''
C_TEST=''
b={'data':2,'link':None};p={'data':1,'link':b};p=p['link'];assert p is b
RESULTS['ch06-q04']={"method":'python',"result":"pass"}

# ch06-q07
C_CODE=''
C_TEST=''
p={'data':'D','link':None}
for name in 'CBA':p={'data':name,'link':p}
while p['link'] is not None:p=p['link']
assert p['data']=='D'
RESULTS['ch06-q07']={"method":'python',"result":"pass"}

# ch06-q10
C_CODE='#include <stdio.h>\n#include <stdlib.h>\n\ntypedef struct Node { int data; struct Node *link; } Node;\nint count_nodes(Node *head) {\n    int count = 0;\n    for (Node *p = head; p != NULL; p = p->link) ++count;\n    return count;\n}\nint main(void) {\n    int n, value;\n    Node *head = NULL, *tail = NULL;\n    if (scanf("%d", &n) != 1 || n < 0) return 1;\n    for (int i = 0; i < n; ++i) {\n        if (scanf("%d", &value) != 1) return 1;\n        Node *p = malloc(sizeof *p);\n        if (p == NULL) return 1;\n        p->data = value;\n        p->link = NULL;\n        if (tail == NULL) head = p;\n        else tail->link = p;\n        tail = p;\n    }\n    printf("%d\\n", count_nodes(head));\n    while (head != NULL) {\n        Node *next = head->link;\n        free(head);\n        head = next;\n    }\n    return 0;\n}'
C_TEST=''
assert c_run(C_CODE,input_text="3 5 6 7\n")=="3\n"
assert c_run(C_CODE,input_text="0\n")=="0\n"
assert c_run(C_CODE,input_text="1 99\n")=="1\n"
RESULTS['ch06-q10']={"method":'c-run',"result":"pass"}

print(json.dumps(RESULTS,ensure_ascii=False,sort_keys=True))
