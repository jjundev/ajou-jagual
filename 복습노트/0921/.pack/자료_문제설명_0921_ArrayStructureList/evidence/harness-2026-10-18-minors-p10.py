# Line-by-line Python re-trace of loops ① and ② in 0921 p10 (no C compiler on host).
# ① all-degree representation
A_deg,A=3,[8,0,7,1]; B_deg,B=3,[10,3,0,1]
C=[0]*4; Apos=Bpos=Cpos=0; degree_a,degree_b=A_deg,B_deg
while Apos<=A_deg and Bpos<=B_deg:
    if degree_a>degree_b: C[Cpos]=A[Apos]; Cpos+=1; Apos+=1; degree_a-=1
    elif degree_a==degree_b: C[Cpos]=A[Apos]+B[Bpos]; Cpos+=1; Apos+=1; Bpos+=1; degree_a-=1; degree_b-=1
    else: C[Cpos]=B[Bpos]; Cpos+=1; Bpos+=1; degree_b-=1
print('① C =',C)
# ② sparse representation: A in terms[0..2], B in terms[3..5]
terms=[(8,3),(7,1),(1,0),(10,3),(3,2),(1,0)]
As,Ae,Bs,Be=0,2,3,5; A0,B0=As,Bs; out=[]; log=[]
while As<=Ae and Bs<=Be:
    ea,eb=terms[As][1],terms[Bs][1]
    c='>' if ea>eb else '=' if ea==eb else '<'
    if c=='>': out.append(terms[As]); att=terms[As]; As+=1
    elif c=='=':
        t=terms[As][0]+terms[Bs][0]; att=None
        if t: att=(t,ea); out.append(att)
        As+=1; Bs+=1
    else: out.append(terms[Bs]); att=terms[Bs]; Bs+=1
    log.append((c,att,As-A0,Bs-B0))
for l in log: print('②',l)
print('② result',out,'A done',As>Ae,'B done',Bs>Be)
assert C==[18,3,7,2]
assert log==[('=',(18,3),1,1),('<',(3,2),1,2),('>',(7,1),2,2),('=',(2,0),3,3)]
print('PASS')
