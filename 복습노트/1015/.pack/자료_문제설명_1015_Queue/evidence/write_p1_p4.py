from pathlib import Path
import html
run=Path('/tmp/ds-explain-1015/review-1015-Queue')
out=run/'explanations'
out.mkdir(exist_ok=True)

def table(headers, rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join(f'<th>{html.escape(str(x))}</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{html.escape(str(x))}</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def zone(kind, cls, title, body):
    return f'<div class="layer {cls}" data-explanation="{kind}"><h4>{title}</h4>{body}</div>'

def sub(k, text):
    return f'<div data-subpart="{k}">{text}</div>'

def summary(first, key, check, concept):
    return '<div class="sum" hidden>'+''.join(f'<div class="summary-group"><h4>{title}</h4><p>{value}</p></div>' for title,value in [('떠올릴 개념·공식',concept),('첫 줄',first),('핵심 판단',key),('검산',check)])+'</div>'

# p1: string 04 is preserved as an item label; the index arithmetic never interprets it.
rows1=[]
front=rear=0
slots=[None]*8
for v in ['10','20','30','04','50','60']:
    rear=(rear+1)%8;slots[rear]=v
    rows1.append((f'넣기 {v}',front,rear,', '.join('·' if x is None else x for x in slots)))
for _ in range(4):
    front=(front+1)%8;v=slots[front];slots[front]=None
    rows1.append((f'삭제 {v}',front,rear,', '.join('·' if x is None else x for x in slots)))
for v in ['70','80','90','100']:
    rear=(rear+1)%8;slots[rear]=v
    rows1.append((f'넣기 {v}',front,rear,', '.join('·' if x is None else x for x in slots)))
p1=''.join([
 zone('understand','eli5','문제를 먼저 읽어요','<p>여덟 칸짜리 원형 줄에서 처음 앞·뒤 표시가 0이에요. 여섯 값을 넣고 넷을 빼고 다시 넷을 넣은 뒤 두 표시의 위치를 구해요.</p>'),
 zone('recall','formal','이 문제를 봤을 때 떠올릴 개념과 공식','<p>“원형 큐”, “크기 8”, “front와 rear”가 단서예요. 이 강의의 원형 큐(circular queue)는 <code>front</code>가 첫 원소 <strong>하나 앞</strong>, <code>rear</code>가 마지막 원소를 가리켜요. 삽입(enqueue)은 rear만 한 칸 옮기고 저장하고, 삭제(dequeue)는 front만 한 칸 옮긴 뒤 그 칸의 값을 읽어요.</p><p>배열 인덱스는 0부터 7까지라 다음 칸은 <code>(현재 인덱스 + 1) % 8</code>이에요. 포화 조건 <code>(rear + 1) % 8 == front</code>를 확인해야 해요. 한 칸을 비워 실제 용량은 7개예요. 이 문제의 최대 점유는 6개라 모든 삽입이 가능해요. 값 <code>04</code>는 원문 그대로 보관하고, 인덱스 계산에는 값의 크기를 쓰지 않아요.</p>'),
 zone('start','formal','첫 줄을 이렇게 써요','<p>종이에 <code>크기 8, front=0, rear=0</code>을 적고, 첫 삽입을 <code>rear=(0+1)%8=1, 1번 칸=10</code>으로 시작해요.</p>'),
 zone('solve','formal','왜 이렇게 푸는지 함께 따라가요',sub('main','<p>넣을 때는 rear만, 뺄 때는 front만 움직여요. 아래 표에서 ·는 현재 큐에 속하지 않는 칸이에요.</p>'+table(['연산','front','rear','0–7번 칸'],rows1)+'<p>삭제 네 번 뒤 front는 4예요. 마지막 네 삽입에서 rear는 6에서 7, 0, 1, 2로 돌아와요. 따라서 <strong>front=4, rear=2</strong>예요.</p>')),
 zone('verify','formal','완성 답과 검산',sub('main','<p>정답은 <strong>front=4, rear=2</strong>예요. 독립 계산으로 front는 삭제 횟수만큼 <code>(0+4)%8=4</code>, rear는 총 삽입 10회만큼 <code>(0+10)%8=2</code>예요. 현재 원소는 6개이고 <code>(2-4+8)%8=6</code>도 맞아요. 큐 순서는 50, 60, 70, 80, 90, 100이에요.</p>')),
 zone('pitfall','warn','여기서 실수하기 쉬워요','<p><code>04</code>를 임의로 <code>40</code>으로 고치지 않아요. 값의 표기는 인덱스 답에 영향을 주지 않아요. 7번 칸 다음 rear는 8이 아니라 0이에요.</p>'),
 zone('retry','formal','설명을 닫고 다시 해 봐요','<ol><li>각 삽입·삭제가 어느 포인터를 움직이는지 적어요.</li><li>7 다음에 0으로 돌아가는 지점을 표시해요.</li><li>마지막 요소 수를 별도로 세어 검산해요.</li></ol>'),
 summary('front=rear=0에서 첫 삽입의 rear를 1로 옮겨요.','삭제 4회와 삽입 10회를 각각 세어 front=4, rear=2예요.','(rear-front+8)%8=6이며 실제 남은 값도 6개예요.','원형 큐: 다음 인덱스=(현재+1)%8, front는 첫 원소 하나 앞이에요.')
])
(out/'p1.html').write_text(p1)

# p2: (b) continues the exact state from (a).
rows2a=[];front=rear=0;slots=[None]*8
for v in ['10','20','30','40','50']:
    rear=(rear+1)%8;slots[rear]=v;rows2a.append((f'넣기 {v}',front,rear))
for _ in range(3):
    front=(front+1)%8;v=slots[front];slots[front]=None;rows2a.append((f'삭제 {v}',front,rear))
rows2b=[]
for v in ['60','70','80','90']:
    rear=(rear+1)%8;slots[rear]=v;rows2b.append((f'넣기 {v}',front,rear))
p2=''.join([
 zone('understand','eli5','문제를 먼저 읽어요','<p>먼저 다섯 값을 줄에 넣고 세 값을 빼요. 그 모습을 그린 뒤, 그 자리에서 네 값을 더 넣고 다시 그려요.</p>'),
 zone('recall','formal','이 문제를 봤을 때 떠올릴 개념과 공식','<p>“크기 8의 원형 큐”, “큐의 모양”, “front와 rear 표시”가 단서예요. 원형 큐(circular queue)에서 <code>front</code>는 첫 원소 하나 앞, <code>rear</code>는 마지막 원소의 칸이에요. 삽입(enqueue)은 <code>rear=(rear+1)%8</code> 뒤 저장하고, 삭제(dequeue)는 <code>front=(front+1)%8</code> 뒤 읽어요.</p><p>그림의 0–7번 칸에 현재 남은 값만 적어요. 빈칸의 오래된 값은 지워 표시해요. 한 칸을 비우는 구현이라 최대 7개이고, (b)의 마지막 점유는 6개라 포화되지 않아요. (b)는 (a) 결과에서 계속해야 해요.</p>'),
 zone('start','formal','첫 줄을 이렇게 써요','<p>(a)의 첫 행을 <code>front=0, rear=0, 모든 칸 비어 있음</code>으로 적고, <code>10 삽입 → rear=1, 1번 칸=10</code>을 채워요. (b)의 첫 행은 (a)의 최종 <code>front=3, rear=5</code>에서 시작해요.</p>'),
 zone('solve','formal','왜 이렇게 푸는지 함께 따라가요',
  sub('a','<p>(a) 다섯 번 삽입할 때 rear만 1부터 5까지 이동해요. 세 번 삭제할 때 front만 1부터 3까지 이동하며 10, 20, 30이 나가요.</p>'+table(['연산','front','rear'],rows2a)+'<p>최종 4번 칸=40, 5번 칸=50이고 다른 칸은 비어요. <strong>front=3, rear=5</strong>예요.</p>'+table(['칸','0','1','2','3','4','5','6','7'],[['값','·','·','·','·','40','50','·','·'],['표시','—','—','—','front','—','rear','—','—']]))+
  sub('b','<p>(b) (a)의 상태를 유지해요. 삽입할 때 rear가 6, 7, 0, 1로 순환해요.</p>'+table(['연산','front','rear'],rows2b)+'<p>최종 4번=40, 5번=50, 6번=60, 7번=70, 0번=80, 1번=90이에요. <strong>front=3, rear=1</strong>이에요.</p>'+table(['칸','0','1','2','3','4','5','6','7'],[['값','80','90','·','·','40','50','60','70'],['표시','—','rear','—','front','—','—','—','—']]))),
 zone('verify','formal','완성 답과 검산',
  sub('a','<p>(a) <strong>front=3, rear=5</strong>, 남은 순서는 40, 50이에요. 독립적으로 점유 수를 계산하면 <code>(5-3+8)%8=2</code>로 그림의 두 값과 맞아요. 원 기출 PDF 1쪽 그림도 3번에 front, 5번에 rear를 표시해요.</p>')+
  sub('b','<p>(b) <strong>front=3, rear=1</strong>, 큐 순서는 40, 50, 60, 70, 80, 90이에요. <code>(1-3+8)%8=6</code>으로 여섯 칸과 맞고, 7번 다음에 0번으로 순환했어요. 원 기출 PDF 2쪽 그림의 위치와 같아요.</p>')),
 zone('pitfall','warn','여기서 실수하기 쉬워요','<p>(b)를 빈 큐에서 다시 시작하면 front가 틀려요. 삭제된 값이 물리적 메모리에 남아 있더라도 현재 큐의 칸으로 그리지 않아요. front가 40이 있는 4번이 아니라 그 앞 3번이라는 점도 확인해요.</p>'),
 zone('retry','formal','설명을 닫고 다시 해 봐요','<ol><li>(a)의 모든 연산에서 front·rear를 갱신해요.</li><li>(a)의 8칸 그림을 완성한 뒤 그대로 (b)를 시작해요.</li><li>두 그림의 원소 수를 인덱스 차이로 검산해요.</li></ol>'),
 summary('(a) front=rear=0에서 rear를 1로 옮기고 10을 넣어요.','(a) front=3, rear=5; 이어서 (b) front=3, rear=1이에요.','(a)는 2개, (b)는 6개가 남아 각각 인덱스 차이와 같아요.','원형 큐: front는 첫 원소 하나 앞, rear는 마지막 칸이에요.')
])
(out/'p2.html').write_text(p2)

# p3 and p4: extract maps options to a-d, so every option receives a solve and verify block.
p3=''.join([
 zone('understand','eli5','문제를 먼저 읽어요','<p>앞 표시가 세 번째 칸, 끝 표시가 다섯 번째 칸에 있어요. 그 사이에 실제 값이 몇 개 있는지 골라요.</p>'),
 zone('recall','formal','이 문제를 봤을 때 떠올릴 개념과 공식','<p>“원형큐”, <code>front=3</code>, <code>rear=5</code>, <code>MAX_QUEUE_SIZE=8</code>이 단서예요. 원형 큐(circular queue)의 <code>front</code>는 첫 원소 하나 앞이에요. 따라서 3번 칸은 세지 않고 4번부터 마지막 원소가 있는 5번까지 세어요.</p><p>순환할 수도 있으므로 일반식은 <code>(rear-front+MAX_QUEUE_SIZE)%MAX_QUEUE_SIZE</code>예요. 여기서는 rear가 front보다 커서 직접 두 칸을 세어도 같아요. 선택지 네 개 중 정확한 개수 하나를 고르면 돼요.</p>'),
 zone('start','formal','첫 줄을 이렇게 써요','<p>종이에 <code>front=3 → 첫 원소는 4번, rear=5 → 마지막 원소는 5번</code>이라고 적어요.</p>'),
 zone('solve','formal','왜 이렇게 푸는지 함께 따라가요',
  sub('a','<p>(a) 1개라면 4번만 있어야 하지만 rear가 5번이므로 맞지 않아요.</p>')+
  sub('b','<p>(b) 4번과 5번, 두 칸이에요. <code>(5-3+8)%8=2</code>이므로 <strong>2개</strong>가 맞아요.</p>')+
  sub('c','<p>(c) 3개는 front가 가리키는 3번까지 세었을 때 생기는 오답이에요. front는 원소 칸이 아니에요.</p>')+
  sub('d','<p>(d) 4개를 얻으려면 3번 이전까지 더 세어야 해요. 주어진 front·rear와 맞지 않아요.</p>')),
 zone('verify','formal','완성 답과 검산',
  sub('a','<p>(a) 1은 실제 칸 4·5 중 하나를 빠뜨려 틀려요.</p>')+
  sub('b','<p>(b) 정답은 <strong>2개</strong>예요. 첫 원소 4번, 마지막 원소 5번을 직접 세어도 2개예요.</p>')+
  sub('c','<p>(c) 3은 3·4·5 세 칸인데 3번은 front라 원소가 아니므로 틀려요.</p>')+
  sub('d','<p>(d) 4는 공식 계산값 <code>(5-3+8)%8=2</code>와 다르므로 틀려요.</p>')),
 zone('pitfall','warn','여기서 실수하기 쉬워요','<p><code>front</code>가 첫 원소를 가리킨다고 생각하면 3개를 고르게 돼요. 강의 슬라이드 S6 p6의 정의는 “첫번째 요소 하나 앞의 인덱스”예요.</p>'),
 zone('retry','formal','설명을 닫고 다시 해 봐요','<ol><li>front가 포함되는 칸인지 말해 봐요.</li><li>4번과 5번을 직접 세어요.</li><li>나머지 공식으로 다시 계산해요.</li></ol>'),
 summary('front=3 다음 칸인 4번부터 적어요.','4번과 5번 두 칸이므로 (b) 2개예요.','(5-3+8)%8=2로 직접 센 수와 같아요.','front는 첫 원소 하나 앞; 원소 수=(rear-front+M)%M이에요.')
])
(out/'p3.html').write_text(p3)

p4=''.join([
 zone('understand','eli5','문제를 먼저 읽어요','<p>둥근 줄에 아무도 없는 상태를 알려 주는 표시를 골라요. 앞·뒤 표시가 어디에서 만나는지 살펴봐요.</p>'),
 zone('recall','formal','이 문제를 봤을 때 떠올릴 개념과 공식','<p>“원형큐에서 공백상태”가 단서예요. 이 강의의 원형 큐(circular queue)는 <code>front</code>가 첫 원소 하나 앞, <code>rear</code>가 마지막 원소예요. 삽입과 삭제를 모두 마치면 위치가 0이 아니어도 두 인덱스가 같아져요.</p><p>따라서 공백(empty)의 조건은 <code>front == rear</code>예요. 포화(full)는 다음 rear가 front에 닿는 <code>(rear+1)%MAX_QUEUE_SIZE == front</code>예요. 둘을 구별하려고 한 칸을 비워요. 보기의 조건이 모든 공백 상태를 잡는지 확인해야 해요.</p>'),
 zone('start','formal','첫 줄을 이렇게 써요','<p>종이에 <code>공백 ⇔ front == rear</code>를 적고, 예로 <code>front=rear=3</code>을 대입해 각 선택지가 모두 성립하는지 살펴봐요.</p>'),
 zone('solve','formal','왜 이렇게 푸는지 함께 따라가요',
  sub('a','<p>(a) <code>front == 0 &amp;&amp; rear == 0</code>은 0에서 비는 경우만 잡아요. 둘 다 3인 공백 상태를 놓치므로 일반 조건이 아니에요.</p>')+
  sub('b','<p>(b) <code>front == MAX_QUEUE_SIZE-1 &amp;&amp; rear == MAX_QUEUE_SIZE-1</code>은 마지막 칸에서 비는 경우만 잡아요. 둘 다 3인 공백 상태를 놓쳐요.</p>')+
  sub('c','<p>(c) <code>front == rear</code>는 같은 위치가 0이든 3이든 모두 공백으로 판정해요. <strong>정답</strong>이에요.</p>')+
  sub('d','<p>(d) <code>front == (rear+1)%MAX_QUEUE_SIZE</code>는 다음 삽입 위치가 front와 같다는 뜻이라 포화 조건이에요.</p>')),
 zone('verify','formal','완성 답과 검산',
  sub('a','<p>(a)에 <code>front=rear=3</code>을 대입하면 거짓이지만 큐는 비어 있어요. 따라서 오답이에요.</p>')+
  sub('b','<p>(b)에도 <code>front=rear=3</code>을 대입하면 거짓이라 공백을 놓쳐요.</p>')+
  sub('c','<p>(c)는 <code>front=rear=0</code>, <code>front=rear=3</code>, <code>front=rear=7</code> 모두 참이에요. 정답은 <strong>(c) front == rear</strong>예요.</p>')+
  sub('d','<p>(d)는 8칸에서 <code>front=3, rear=2</code>를 넣으면 <code>3==(2+1)%8</code>로 참이고 점유 수는 <code>(2-3+8)%8=7</code>이에요. 즉 공백이 아니라 포화예요.</p>')),
 zone('pitfall','warn','여기서 실수하기 쉬워요','<p>초기값이 0이라고 해서 공백이 항상 0에서만 생기지는 않아요. 삭제를 마치면 두 인덱스가 다른 위치에서도 같아질 수 있어요.</p>'),
 zone('retry','formal','설명을 닫고 다시 해 봐요','<ol><li>초기 위치 외의 공백 예를 하나 만들어요.</li><li>각 보기에 그 값을 대입해요.</li><li>포화 조건과 공백 조건을 구분해요.</li></ol>'),
 summary('공백 ⇔ front == rear를 먼저 적어요.','모든 위치의 공백을 잡는 (c)를 골라요.','front=rear=3은 (a)·(b)를 반박하고, front=3·rear=2는 (d)가 포화임을 보여 줘요.','공백: front == rear; 포화: (rear+1)%MAX_QUEUE_SIZE == front예요.')
])
(out/'p4.html').write_text(p4)
print(*(str(out/f'p{i}.html') for i in range(1,5)),sep='\n')
