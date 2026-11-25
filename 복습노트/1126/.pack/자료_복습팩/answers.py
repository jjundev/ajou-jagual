from collections import deque

def partition(data, left, right):
    pivot = data[left]
    lo, hi = left, right + 1
    swaps = []
    while True:
        lo += 1
        while lo <= right and data[lo] < pivot:
            lo += 1
        hi -= 1
        while data[hi] > pivot:
            hi -= 1
        if lo >= hi:
            break
        data[lo], data[hi] = data[hi], data[lo]
        swaps.append((lo, hi, data.copy()))
    data[left], data[hi] = data[hi], data[left]
    if left != hi:
        swaps.append((left, hi, data.copy()))
    return hi, swaps

def quick_levels(data):
    levels = []
    ranges = [(0, len(data)-1)]
    fixed = []
    while ranges:
        following = []
        pivots = []
        for left,right in ranges:
            pivots.append(data[left])
            q,_ = partition(data,left,right)
            fixed.append(q)
            following += [(a,b) for a,b in [(left,q-1),(q+1,right)] if a < b]
        next_pivots = [a for a,b in following]
        levels.append((pivots,data.copy(),sorted(fixed),next_pivots,following))
        ranges = following
    return levels

def quick_tree(data,left,right,swaps):
    if left > right:
        return None
    if left == right:
        return (data[left],None,None)
    q, changes = partition(data,left,right)
    swaps.extend(changes)
    return (data[q],quick_tree(data,left,q-1,swaps),quick_tree(data,q+1,right,swaps))

def shell(data,gaps):
    stages=[]
    for gap in gaps:
        for i in range(gap,len(data)):
            key=data[i]
            j=i-gap
            while j>=0 and data[j]>key:
                data[j+gap]=data[j]
                j-=gap
            data[j+gap]=key
        stages.append(data.copy())
    return stages

def insertion_descending_swaps(data):
    states=[]
    for i in range(1,len(data)):
        j=i
        while j>0 and data[j-1]<data[j]:
            data[j-1],data[j]=data[j],data[j-1]
            states.append(data.copy())
            j-=1
    return states

def selection(data, passes):
    for i in range(passes):
        j=min(range(i,len(data)),key=data.__getitem__)
        data[i],data[j]=data[j],data[i]
    return data

def bubble(data, passes):
    comparisons=moves=0
    for end in range(len(data)-1,len(data)-1-passes,-1):
        for i in range(end):
            comparisons+=1
            if data[i]>data[i+1]:
                data[i],data[i+1]=data[i+1],data[i]
                moves+=3
    return data,comparisons,moves

def merge(left,right,stable=True):
    result = []
    trace = []
    i = j = 0
    while i < len(left) and j < len(right):
        a,b = left[i][0],right[j][0]
        if a < b or (stable and a == b):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
        trace.append((i,j,result.copy()))
    return result + left[i:] + right[j:], trace

def insertion_counts(data):
    compares=moves=0
    for i in range(1,len(data)):
        key=data[i]
        moves+=1
        j=i-1
        while j>=0:
            compares+=1
            if data[j]<=key:
                break
            data[j+1]=data[j]
            moves+=1
            j-=1
        data[j+1]=key
        moves+=1
    return data,compares,moves

def rows(states):
    return ' / '.join(' '.join(map(str,s)) for s in states)

def list_tree(tree):
    value,left,right=tree
    desc=[f'{value}→'+', '.join(str(child[0]) for child in (left,right) if child)] if left or right else []
    for child in (left,right):
        if child:
            desc.extend(list_tree(child))
    return desc

def calculate():
    q1=quick_levels([27,4,37,2,62,12,59,16,49,18])
    q2a=shell([14,5,43,27,18,31,37,88,6,35],[5,3,1])
    q2b=quick_tree([9,73,42,1,80,39,72,30,100,46,82,32,17],0,12,[])
    q3=insertion_descending_swaps([7,4,9,6,3,8])
    swaps=[]
    quick_tree([25,3,50,72,9,46,15],0,6,swaps)
    sel=[(2,'A'),(2,'B'),(1,'')]
    sel[0],sel[2]=sel[2],sel[0]
    input_insertion_costs()
    best=bubble([1,2,3,4,5],4)
    worst=bubble([5,4,3,2,1],4)
    merged,trace=merge([(2,''),(5,'A'),(7,'')],[(1,''),(4,''),(5,'B')])
    assert merged==[(1,''),(2,''),(4,''),(5,'A'),(5,'B'),(7,'')]
    assert len(trace)==5
    right_first,_=merge([(5,'A')],[(5,'B')],stable=False)
    assert right_first==[(5,'B'),(5,'A')]
    right_order=' '.join(f'{key}{tag}' for key,tag in right_first)
    merge_levels=(8).bit_length()-1
    copy_each_level=2*8
    assert (merge_levels,copy_each_level,merge_levels*copy_each_level)==(3,16,48)
    q8=bubble([9,6,7,3,5],1)[0]
    q9=selection([8,3,4,9,7],3)
    tests=([3,2,1],[2,2,1],[1,2,3],[1],[])
    assert all(insertion_counts(list(a))[0]==sorted(a) for a in tests)
    return [
        ' / '.join(' '.join(f'({v})' if i in nxt else str(v) for i,v in enumerate(row)) for _,row,_,nxt,_ in q1),
        rows(q2a)+' / '+' · '.join(list_tree(q2b)),
        rows(q3),
        rows([state for _,_,state in swaps]),
        f"선택 {sel[1][0]}{sel[1][1]} {sel[2][0]}{sel[2][1]} (불안정) / 삽입 2A 2B (안정)",
        f"비교 {best[1]}회·이동 {best[2]}회 / 비교 {worst[1]}회·이동 {worst[2]}회",
        f'1 2 4 5A 5B 7 / 비교 {len(trace)}회 / 7 복사 / 오른쪽 우선 {right_order} / {merge_levels}패스·{merge_levels*copy_each_level}회 이동',
        '② '+rows([q8]),
        '① '+rows([q9]),
        '④ (4) / j>=0 && key < A[j] / A[j+1]=A[j];',
        '2번 / 어느 정도 정렬되어 있다.'
    ]

def input_insertion_costs():
    a=insertion_counts([1,2,3,4,5])
    b=insertion_counts([5,4,3,2,1])
    assert a[1:]==(4,8)
    assert b[1:]==(10,18)
    return a,b

def verify_insertion_c():
    import os
    from pathlib import Path
    import shutil
    import subprocess
    import tempfile

    compiler=shutil.which('cc') or shutil.which('gcc') or shutil.which('clang')
    if compiler is None:
        raise RuntimeError('C11 compiler not found')
    original = """void sort(int A[], int n)
{
    int i, j, key;
    for (i=1; i<n; i++) {
        key=A[i];
        for (j=i-1; ㉠ ; j--)
            ㉡
        A[j+1]=key;
    }
}"""
    options = [
        ('j>=0 && key > A[j]','A[j+1]=A[j];'),
        ('j>0 && key >= A[j]','A[j-1]=A[j];'),
        ('j>0 && key < A[j]','A[j]=A[j+1];'),
        ('j>=0 && key < A[j]','A[j+1]=A[j];'),
    ]
    harness = r"""
#include <stdio.h>
int main(void) {
    int A[] = {2,1};
    int B[] = {4,2,3,2,1};
    sort(A, 2);
    sort(B, 5);
    printf("%d %d / %d %d %d %d %d\n", A[0],A[1],B[0],B[1],B[2],B[3],B[4]);
    return 0;
}
"""
    with tempfile.TemporaryDirectory(prefix='insertion-c11-',dir=os.environ.get('DS_1126_VERIFY_TEMP')) as temp:
        temp=Path(temp)
        results=[]
        for label,(cond,move) in enumerate(options,1):
            src=temp/f'choice{label}.c'
            exe=temp/(f'choice{label}.exe' if os.name=='nt' else f'choice{label}')
            src.write_text(original.replace('㉠',cond).replace('㉡',move)+harness,encoding='ascii')
            subprocess.run([compiler,'-std=c11','-Wall','-Wextra','-Werror',str(src),'-o',str(exe)],check=True)
            got=subprocess.check_output([str(exe)],text=True).strip()
            results.append(got)
            print(f'P10 option {label}: {got}')
        assert [i+1 for i,got in enumerate(results) if got=='1 2 / 1 2 2 3 4']==[4]

if __name__=='__main__':
    import sys

    for number,answer in enumerate(calculate(),1):
        print(f'P{number}: {answer}')
    if '--c-check' in sys.argv:
        verify_insertion_c()


