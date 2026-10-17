"""Reproduce traces for restored exams; the uncorrected UB loop is never run."""
import math

def foo(x,y):
    return y if x%y==0 else foo(y,x%y)

def loop_count(n,start,width,inclusive):
    count=0
    for i in range(start,n):
        j=start
        while j<n:
            while (j<=i if inclusive else j<i):
                count+=width
                j+=1
            j+=1
    return count

def queue_trace(operations):
    a=[None]*8;front=rear=0
    for op in operations:
        if op is None:
            assert front!=rear
            front=(front+1)%8;a[front]=None
        else:
            assert (rear+1)%8!=front
            rear=(rear+1)%8;a[rear]=op
    return front,rear,a

def verify():
    for x in range(1,80):
        for y in range(1,80):assert foo(x,y)==math.gcd(x,y)
    for n in range(1,30):
        assert loop_count(n,0,30,False)==30*n*(n-1)//2
        assert loop_count(n,1,29,True)==29*n*(n-1)//2
    stack=[];states=[]
    for token in '7 6 2 / - 5 4 * +'.split():
        if token.isdigit():stack.append(int(token))
        else:
            right,left=stack.pop(),stack.pop()
            stack.append({'/':lambda:left//right,'-':lambda:left-right,'*':lambda:left*right,'+':lambda:left+right}[token]())
        states.append(list(stack))
    assert states==[[7],[7,6],[7,6,2],[7,3],[4],[4,5],[4,5,4],[4,20],[24]]
    a=queue_trace([10,20,30,40,50]+[None]*3)
    b=queue_trace([10,20,30,40,50]+[None]*3+[60,70,80,90])
    c=queue_trace([10,20,30,4,50,60]+[None]*4+[70,80,90,100])
    assert a==(3,5,[None,None,None,None,40,50,None,None])
    assert b==(3,1,[80,90,None,None,40,50,60,70])
    assert c==(4,2,[80,90,100,None,None,50,60,70])
    print('PASS: GCD 6241 inputs; corrected/original finite loop counts n=1..29; all postfix states; all circular queue cells and indices')
    print('2019-mid-q9 raw code excluded from execution: k stays zero; n>=2 cannot claim defined normal termination.')

if __name__=='__main__':verify()
