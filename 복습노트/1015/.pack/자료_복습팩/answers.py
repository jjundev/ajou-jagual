"""Reproduce eight answers without changing repository; C compiler required."""
from collections import deque
from pathlib import Path
import json,subprocess,tempfile

def circular(ops,m=8):
    a=[None]*m;f=r=0;trace=[]
    for op,v in ops:
        if op=='in':
            assert (r+1)%m!=f
            r=(r+1)%m;a[r]=v
        else:
            assert f!=r
            f=(f+1)%m;a[f]=None
        trace.append(dict(op=op,value=v,front=f,rear=r,slots=a.copy()))
    return f,r,a,trace

def main():
    p1=circular([('in',x) for x in [10,20,30,4,50,60]]+[('out',None)]*4+[('in',x) for x in [70,80,90,100]])
    assert p1[:2]==(4,2)
    a=circular([('in',x) for x in [10,20,30,40,50]]+[('out',None)]*3)
    b=circular([('in',x) for x in [10,20,30,40,50]]+[('out',None)]*3+[('in',x) for x in [60,70,80,90]])
    assert a[:2]==(3,5) and b[:2]==(3,1)
    assert b[2]==[80,90,None,None,40,50,60,70]
    # Verify occupancy and empty conditions for every valid index pair.
    for f in range(8):
        for r in range(8):
            n=(r-f+8)%8
            assert (n==0)==(f==r)
    assert (5-3+8)%8==2
    src=r'''
#include <assert.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>
#define MAX_QUEUE_SIZE 8
#define CAP 256
typedef struct {int front,rear;} QueueType;
int get_count(const QueueType *q) {
    return (q->rear - q->front + MAX_QUEUE_SIZE) % MAX_QUEUE_SIZE;
}
typedef struct {int a[CAP],top;} Stack;
typedef struct {Stack in,out;} TwoStackQueue;
int enqueue(TwoStackQueue *q,int value) {
    if(q->in.top+q->out.top>=CAP) return 0;
    q->in.a[q->in.top++]=value;
    return 1;
}
int dequeue(TwoStackQueue *q,int *value) {
    if(q->out.top==0) {
        while(q->in.top>0) q->out.a[q->out.top++]=q->in.a[--q->in.top];
    }
    if(q->out.top==0) return 0;
    *value=q->out.a[--q->out.top];return 1;
}
#include <locale.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include <wctype.h>
#define CAP 256
/* UTF-8 로캘에서 1=회문, 0=비회문, -1=입력·로캘 오류/용량 초과 */
int is_palindrome(const char *s) {
    if (!s) return -1;
    const char *loc = setlocale(LC_CTYPE, "");
    if (!loc || !(strstr(loc, "UTF-8") || strstr(loc, "utf8"))) return -1;
    wchar_t d[CAP];
    size_t head = 0, tail = 0, i = 0;
    mbstate_t state = {0};
    while (s[i] != '\0') {
        wchar_t ch;
        size_t n = mbrtowc(&ch, s + i, strlen(s + i), &state);
        if (n == (size_t)-1 || n == (size_t)-2 || n == 0) return -1;
        if (iswalnum(ch)) {
            if (tail == CAP) return -1;
            d[tail++] = towlower(ch);
        }
        i += n;
    }
    while (tail - head > 1) {
        if (d[head++] != d[--tail]) return 0;
    }
    return 1;
}
int main(void) {
    QueueType q;
    for(q.front=0;q.front<8;++q.front)
        for(q.rear=0;q.rear<8;++q.rear) {
            int count=0,i=q.front;
            while(i!=q.rear) {i=(i+1)%8;++count;}
            assert(get_count(&q)==count);
        }
    TwoStackQueue t={0};int v;
    assert(!dequeue(&t,&v));
    assert(enqueue(&t,10)&&enqueue(&t,20)&&enqueue(&t,30));
    assert(dequeue(&t,&v)&&v==10);
    assert(enqueue(&t,40));
    assert(dequeue(&t,&v)&&v==20);
    assert(dequeue(&t,&v)&&v==30);
    assert(dequeue(&t,&v)&&v==40);
    assert(!dequeue(&t,&v));
    const char *yes[]={"eye","madam","radar","A man, a plan, a canal: Panama!","","a","Aa"};
    for(size_t i=0;i<sizeof yes/sizeof *yes;++i) assert(is_palindrome(yes[i])==1);
    assert(is_palindrome("hello")==0);
    assert(is_palindrome("가나")==0);
    assert(is_palindrome("가나다가")==0);
    assert(is_palindrome("가나다나가")==1);
    assert(is_palindrome("한글글한")==1);
    assert(is_palindrome("\xff")==-1);
    char too_long[CAP+2];memset(too_long,'a',CAP+1);too_long[CAP+1]='\0';
    assert(is_palindrome(too_long)==-1);
    puts("p6: 64 front/rear pairs pass; p7: interleaved FIFO and empty pass; p8: case/punctuation/odd/even/empty/capacity pass");
}
'''
    with tempfile.TemporaryDirectory(prefix='ds1015-answers-') as tmp:
        p=Path(tmp);(p/'verify.c').write_text(src)
        subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(p/'verify.c'),'-o',str(p/'verify')],check=True)
        out=subprocess.check_output([str(p/'verify')],text=True).strip()
    result=dict(p1=p1,p2a=a,p2b=b,p3='(b) 2개',p4='(c) front == rear',p5='(a) O(1)',c_verification=out)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
