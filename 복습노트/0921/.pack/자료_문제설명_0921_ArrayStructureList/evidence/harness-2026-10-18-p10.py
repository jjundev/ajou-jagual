# ① 모든 차수 방식 루프 (degree, coef 내림차순)
A=dict(degree=3,coef=[8,0,7,1]); B=dict(degree=3,coef=[10,3,0,1]); C=[]
Apos=Bpos=0; da=A['degree']; db=B['degree']
while Apos<=A['degree'] and Bpos<=B['degree']:
    if da>db: C.append(A['coef'][Apos]); Apos+=1; da-=1
    elif da==db: C.append(A['coef'][Apos]+B['coef'][Bpos]); Apos+=1; Bpos+=1; da-=1; db-=1
    else: C.append(B['coef'][Bpos]); Bpos+=1; db-=1
print('dense',C)
# ② 희소 방식 switch
terms=[(8,3),(7,1),(1,0),(10,3),(3,2),(1,0)]; As,Ae,Bs,Be=0,2,3,5; out=[];log=[]
while As<=Ae and Bs<=Be:
    a,b=terms[As][1],terms[Bs][1]
    if a>b: out.append(terms[As]); As+=1; log.append('>:A')
    elif a==b:
        t=terms[As][0]+terms[Bs][0]
        if t: out.append((t,a))
        As+=1;Bs+=1; log.append('=:AB')
    else: out.append(terms[Bs]); Bs+=1; log.append('<:B')
print('sparse',out,log,'leftA',Ae-As+1,'leftB',Be-Bs+1)
