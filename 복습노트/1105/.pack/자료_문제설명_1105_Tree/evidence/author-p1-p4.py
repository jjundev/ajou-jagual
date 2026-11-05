from pathlib import Path
from html import escape
import json
import hashlib
import unicodedata

F = Path('/tmp/ds-problem-explain-1105-20261105-v2/review-1105-Tree')
R = Path('/tmp/ds-review-pack-1105-20261105')
REPO = R/'repo'
ind = json.loads((F/'evidence/independent-results.json').read_text())['answers']
auth = json.loads((F/'evidence/answer-data.json').read_text())['problems']


def layer(kind,title,body):
    cls = {'understand':'eli5','pitfall':'warn'}.get(kind,'formal')
    return f'<div class="layer {cls}" data-explanation="{kind}">\n<h4>{title}</h4>\n{body}\n</div>\n'


def main(body):
    return '<div data-subpart="main">\n'+body+'\n</div>'


def block(text):
    return '<pre><code>'+escape(text)+'</code></pre>'


def table(heads,rows):
    return '<table><thead><tr>'+''.join('<th scope="col">'+str(h)+'</th>' for h in heads)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table>'


def array30(arr):
    arr = {int(i):v for i,v in arr.items()}
    return table(['칸','값','칸','값','칸','값'],[[i,arr.get(i,'빈칸'),i+10,arr.get(i+10,'빈칸'),i+20,arr.get(i+20,'빈칸')] for i in range(1,11)])


def summary(groups):
    return '<div class="sum" hidden>\n'+''.join('<div class="summary-group"><h4>'+title+'</h4>'+body+'</div>\n' for title,body in groups)+'</div>\n'


def ascii_relations(snapshot):
    rel=snapshot['relations']
    def visit(k,depth=0,label='root'):
        lines=['  '*depth+label+': '+str(k)]
        item=rel[str(k)]
        for field,label2 in [('left','L'),('right','R')]:
            if item[field] is not None:lines+=visit(item[field],depth+1,label2)
        return lines
    return '\n'.join(visit(snapshot['root']))


def treeblock(snapshot):
    return block(ascii_relations(snapshot))


def seq(xs):return ' '.join(map(str,xs))


parts=[]
parts.append(layer('understand','어떤 연결을 바꾸라는 문제일까요?',
    '<p>한 트리에 삭제를 세 번 이어서 해요. 앞의 삭제가 끝난 트리를 다음 삭제의 출발점으로 삼고, 지우라고 한 키만 없어지게 해야 해요.</p>'
    '<p>마지막 5는 두 자식을 가지므로 오른쪽 최솟값을 쓰는 답과 왼쪽 최댓값을 쓰는 답을 각각 만들 수 있어요.</p>'))
parts.append(layer('recall','이 문제를 봤을 때 떠올릴 개념과 공식',
    '<p>‘이진 탐색 트리에서 순차적으로 delete’라는 단서에서는 <strong>BST(binary search tree)의 순서 보존과 자식 수에 따른 삭제</strong>를 떠올려요. BST는 각 노드의 왼쪽 서브트리 전체가 그 키보다 작고 오른쪽 전체가 커야 하며, 키는 중복되지 않아요.</p>'
    '<p>삭제 대상의 자식이 0개면 단말 노드(leaf node)라서 부모의 해당 링크를 <code>NULL</code>로 바꿔요. 1개면 부모가 그 유일한 자식을 직접 가리키게 해요. 자식 하나뿐 아니라 그 아래 서브트리도 보존하는 방법이에요.</p>'
    '<p>자식이 2개면 오른쪽 서브트리의 최솟값인 후계자(successor) 또는 왼쪽 서브트리의 최댓값인 선행자(predecessor)로 대체해요. 후계자는 오른쪽으로 한 번 간 뒤 왼쪽 끝까지, 선행자는 왼쪽으로 한 번 간 뒤 오른쪽 끝까지 찾아요.</p>'
    '<p>후계자보다 작은 값은 오른쪽에 남지 않고 선행자보다 큰 값은 왼쪽에 남지 않으므로 엄격한 순서를 지킬 수 있어요. 대체값을 복사해 놓고 끝내면 키가 두 개 남으니 <strong>후보의 원래 자리도 삭제</strong>해야 해요. 후계자에게 오른쪽 자식이 있다면 그 자식은 후보의 부모에게 이어 붙여요.</p>'))
parts.append(layer('start','종이에 쓰는 실제 첫 줄',
    '<p>먼저 첫 삭제 대상의 부모와 두 자식을 적어요.</p>'
    +block('13: parent=12, left=NULL, right=NULL')+
    '<p>따라서 첫 작업은 <code>12의 오른쪽 링크 = NULL</code>이에요. 16이나 5의 처리를 미리 섞지 않고, 13만 지운 상태부터 그려요.</p>'))
solve='<p>아래 상태는 빈 링크를 생략한 트리 표현이에요. <code>L</code>은 바로 윗줄 부모의 왼쪽 자식, <code>R</code>은 오른쪽 자식이며 들여쓰기가 깊이를 나타내요. 적히지 않은 자식 링크는 <code>NULL</code>이에요.</p>'
solve+='<h5>1. 13 삭제: 자식 0개</h5><p>15에서 왼쪽 5, 오른쪽 12, 오른쪽 13으로 찾아가요. 13에는 남길 자식이 없으므로 12의 오른쪽만 비워요. 다른 가지는 옮기지 않아요.</p>'+treeblock(ind['p1']['conventions']['successor'][0]['tree'])
solve+='<h5>2. 16 삭제: 자식 1개</h5><p>이제 루트 15의 오른쪽에서 16을 찾아요. 왼쪽은 비어 있고 오른쪽에는 20이 있으므로, <code>15의 오른쪽 = 20</code>으로 바꿔요. 20의 자식 18과 23은 20에 달린 채로 따라와요.</p>'+treeblock(ind['p1']['conventions']['successor'][1]['tree'])
solve+='<h5>3. 5 삭제: 후계자 6을 쓰는 방법</h5><p>현재 5의 왼쪽에는 3, 오른쪽에는 12가 있어요. 자식이 둘이므로 5를 그냥 끊으면 두 가지를 함께 잃어요. 오른쪽 서브트리에서 <code>12 → 10 → 6</code>으로 왼쪽 끝까지 가면 최솟값 6을 찾아요.</p><p>5 자리에 키 6을 두어요. 원래 6은 왼쪽이 비어 있지만 오른쪽 자식 7이 있으므로, 원래 6의 부모 10이 7을 이어받게 <code>10의 왼쪽 = 7</code>로 바꿔요. 이것이 후보 원래 자리의 한 자식 삭제예요.</p>'+treeblock(ind['p1']['conventions']['successor'][2]['tree'])
solve+='<h5>같은 3단계에서 선행자 3을 쓰는 방법</h5><p>16까지 삭제한 상태로 돌아가서 다른 정답을 만들어요. 5의 왼쪽 서브트리는 3 하나이므로 최댓값도 3이에요. 5 자리에 3을 두고 원래 단말 3을 없애 새 3의 왼쪽을 <code>NULL</code>로 바꿔요. 오른쪽의 <code>12 → 10 → 6 → 7</code> 가지는 그대로 남아요.</p>'+treeblock(ind['p1']['conventions']['predecessor'][2]['tree'])
solve+='<p>두 방법의 13·16 삭제 결과는 같고, 마지막 5의 대체 후보만 달라요. 어느 방법이든 마지막 노드 수는 9개예요.</p>'
parts.append(layer('solve','왜 이렇게 푸는지 함께 따라가요',main(solve)))
parts.append(layer('verify','완성 답과 검산',main(
    '<p>완성 답은 위의 두 최종 트리예요. 후계자 답의 핵심 연결은 <code>15의 왼쪽 6, 6의 왼쪽 3·오른쪽 12, 12의 왼쪽 10, 10의 왼쪽 7</code>이에요. 선행자 답은 <code>15의 왼쪽 3, 3의 오른쪽 12, 12의 왼쪽 10, 10의 왼쪽 6, 6의 오른쪽 7</code>이에요. 두 답 모두 15의 오른쪽은 20이고 20의 왼쪽 18·오른쪽 23이 남아요.</p>'
    '<p>독립 삭제 시뮬레이션에서도 세 번의 중간 상태와 두 최종 연결이 모두 같았어요. 마지막 두 트리를 각각 중위 순회(inorder traversal, LVR)한 출력은 같아요.</p>'
    +block('3 6 7 10 12 15 18 20 23')+
    '<p>원래 12개 키에서 13·16·5만 뺀 9개가 오름차순으로 나와요. 각 노드에 조상부터 내려온 허용 범위를 적용한 검사도 통과했어요. 특히 후계자 답에서 <code>6 &lt; 7 &lt; 10</code>이므로 7은 새 6의 오른쪽 서브트리이자 10의 왼쪽에 올 수 있어요. 선행자 답은 원래 6의 오른쪽 7을 그대로 보존했어요.</p>')))
parts.append(layer('pitfall','이 문제에서 특히 조심할 점',
    '<p>13·16·5는 세 소문항이 아니라 한 트리에 이어서 하는 연산이에요. 매번 원래 그림으로 돌아가면 다른 결과를 만들어요.</p>'
    '<p>후계자를 12라고 정하면 안 돼요. 오른쪽 자식은 12지만 오른쪽 서브트리 최솟값은 더 내려간 6이에요. 6을 옮겼다고 7도 지우거나 10의 왼쪽을 비우면 남겨야 할 키 하나를 잃어요.</p>'
    '<p>대체 후보를 옮긴 뒤 원래 후보도 정리해야 중복 키가 남지 않아요. 선행자 3을 쓰는 답도 가능하므로 후계자 답과 모양이 다르다는 이유만으로 틀렸다고 판단하지 않아요.</p>'))
parts.append(layer('retry','해설을 닫고 다시 해 봐요',
    '<ol><li>13·16·5의 자식 수를 연산 순서대로 판단하고 매번 바뀌는 링크 하나씩 표시해요.</li><li>5의 후계자를 직접 찾아 원래 6의 오른쪽 자식 7이 어디로 가는지 설명해요.</li><li>선행자 답도 그리고 두 답의 중위 순회가 같은지 확인해요.</li></ol>'))
parts.append(summary([
    ('떠올릴 개념·공식','<p>BST는 키가 유일하고 왼쪽 전체 &lt; 현재 키 &lt; 오른쪽 전체예요. 삭제는 자식 0개·1개·2개로 나눠요. 2개면 오른쪽 최소 후계자 또는 왼쪽 최대 선행자를 쓰고 원래 후보 자리도 정리해요.</p>'),
    ('첫 줄','<p>13의 부모는 12, 두 자식은 NULL이에요. 먼저 12의 오른쪽을 NULL로 바꿔요.</p>'),
    ('핵심 판단','<p>같은 트리에 13 → 16 → 5를 이어서 삭제해요. 16 대신 20을 연결해 18·23을 보존해요. 후계자 6을 쓰면 원래 6의 오른쪽 7을 10의 왼쪽에 연결해요. 선행자 3을 쓰면 6·7은 원래 가지에 남아요. 두 최종 모양 모두 가능해요.</p>'),
    ('검산','<p>12개 중 13·16·5만 없어져 9개예요. 두 답 모두 중위 출력은 3 6 7 10 12 15 18 20 23이고 전체 조상 범위를 만족해요. 대체 키 중복·남길 서브트리 손실이 없어야 해요.</p>')]))
(F/'explanations/p1.html').write_text(''.join(parts))


parts=[]
parts.append(layer('understand','어떤 결과를 배열에 써야 할까요?',
    '<p>키를 받은 순서대로 BST에 넣고, 두 키를 삭제한 최종 연결을 배열로 옮기는 문제예요. 배열의 값 순서는 정렬 순서가 아니라 트리에서 차지하는 자리 순서예요.</p>'))
parts.append(layer('recall','이 문제를 봤을 때 떠올릴 개념과 공식',
    '<p>‘주어진 순서대로 만든 다음 삭제’라는 표현에서는 <strong>BST 삽입(insert) → 자식 수에 따른 삭제(delete)</strong>를 떠올려요. 새 키가 현재 키보다 작으면 왼쪽, 크면 오른쪽으로 가며, 처음 만나는 빈 링크가 그 키의 자리예요. 중복 키는 넣지 않는 규칙이고, 이 문제의 12개 키는 모두 달라요.</p>'
    '<p>‘배열로 표현’이라는 단서에서는 <strong>1번을 루트로 하는 위치 번호</strong>를 떠올려요. 배열을 $A$, 부모 칸 번호를 $i$라고 하면 왼쪽 자식은 $A[2i]$, 오른쪽 자식은 $A[2i+1]$에 놓아요. $i$는 키값이 아니라 칸 번호예요.</p>'
    '<p>이 규칙은 빈칸까지 포함해 트리 모양을 보존해요. 삭제 대상에게 자식이 하나면 그 자식을 부모에게 연결한 뒤 새 연결로 칸 번호를 다시 정해야 해요. 원래 배열에서 삭제한 숫자만 지우는 방법으로는 그 이동을 표현하지 못해요.</p>'))
parts.append(layer('start','종이에 쓰는 실제 첫 줄',
    block('A[1] = 520')+
    '<p>빈 트리에서 첫 키 520이 루트가 돼요. 다음 키 490은 520보다 작으므로 520의 왼쪽, 즉 <code>A[2] = 490</code>을 이어 적어요. 이처럼 키마다 루트부터 비교하고 끝난 링크를 기록해요.</p>'))
rows=[]
for n,s in enumerate(auth['p2']['insertions'],1):
    k=s['insert'];path=s['comparison_path'];arr=s['array'];i=next(int(i) for i,v in arr.items() if v==k)
    parent=path[-1] if path else None
    link='root' if parent is None else f'{parent}의 '+('왼쪽' if k<parent else '오른쪽')
    rows.append([n,k,' → '.join(map(str,path)) if path else '빈 트리',link,f'A[{i}]={k}'])
solve='<h5>1. 12번 삽입을 차례로 누적해요</h5><p>표의 비교 경로는 삽입 직전의 기존 노드예요. 매 행마다 표시한 빈 링크에 새 노드 하나를 붙이고, 앞 행에서 만든 다른 링크는 그대로 두어요. 따라서 1행부터 누적하면 각 삽입 직후의 전체 상태가 정해져요.</p>'
solve+=table(['차례','새 키','비교 경로','새로 붙이는 링크','삽입 직후 칸'],rows)
solve+='<p>예를 들어 280은 520·490·380보다 작아서 왼쪽으로 내려가지만, 250보다 크므로 마지막에는 오른쪽으로 가요. 그래서 380의 왼쪽을 덮어쓰는 것이 아니라 <code>250의 오른쪽</code>에 붙어요. 580은 570보다 크고 610보다 작으므로 <code>610의 왼쪽</code>에 붙어요.</p>'
solve+='<h5>2. 250만 먼저 삭제해요</h5><p>250의 왼쪽은 비었고 오른쪽에는 280만 있어요. 부모 380의 왼쪽이 250 대신 280을 가리키게 해요. 그러면 280의 칸은 17에서 8로 바뀌고 17번은 비어요. 다른 가지는 그대로예요.</p>'
solve+=table(['연산','바꾸는 연결','이 단계 뒤 비어 있지 않은 칸'],[
    ['250 삭제','380의 왼쪽 = 280','1:520, 2:490, 3:650, 4:380, 6:570, 8:280, 9:450, 13:610, 18:430, 19:460, 26:580']])
solve+='<h5>3. 이어서 610을 삭제해요</h5><p>610에는 왼쪽 자식 580만 있어요. 부모 570의 오른쪽이 580을 직접 가리키게 해요. 570은 6번 칸이므로 그 오른쪽 580의 새 칸은 $2\\times6+1=13$이에요. 원래 26번은 비워요.</p>'
solve+=table(['연산','바꾸는 연결','이 단계 뒤 비어 있지 않은 칸'],[
    ['610 삭제','570의 오른쪽 = 580','1:520, 2:490, 3:650, 4:380, 6:570, 8:280, 9:450, 13:580, 18:430, 19:460']])
solve+='<h5>4. 바뀐 트리를 배열 답으로 옮겨요</h5><p>450은 9번이어서 그 왼쪽 430은 18번, 오른쪽 460은 19번이에요. 490의 오른쪽 자식은 없으므로 5번을 비우고 570을 6번에 놓아요. 빈칸을 앞으로 당기지 않아요.</p>'+array30(ind['p2']['steps'][-1]['tree']['sparse_1based_array'])
parts.append(layer('solve','왜 이렇게 푸는지 함께 따라가요',main(solve)))
parts.append(layer('verify','완성 답과 검산',main(
    '<p>정답의 비어 있지 않은 칸은 <code>1:520, 2:490, 3:650, 4:380, 6:570, 8:280, 9:450, 13:580, 18:430, 19:460</code>이에요. 1~30 중 나머지는 모두 빈칸이에요.</p>'
    '<p>독립 삽입·삭제 시뮬레이션과 비교해 12번 삽입 뒤의 연결, 두 삭제 뒤의 연결과 배열이 일치했어요. 최종 노드 수는 $12-2=10$개예요. 280·580은 남고 삭제 대상 250·610만 없어졌어요.</p>'
    '<p>배열의 위치를 링크로 다시 읽으면 <code>380의 왼쪽 280·오른쪽 450</code>, <code>570의 오른쪽 580</code>, <code>450의 왼쪽 430·오른쪽 460</code>이에요. 중위 순회 결과도 다음 오름차순이에요.</p>'
    +block('280 380 430 450 460 490 520 570 580 650')+
    '<p>각 키의 조상 범위까지 검사해 순서를 확인했어요. 예를 들어 580은 570보다 크고 650보다 작아 그 사이 가지에 남아요.</p>')))
parts.append(layer('pitfall','배열의 빈칸을 없애면 안 돼요',
    '<p>정렬된 키를 1번부터 쓰면 BST의 위치를 표현하지 못해요. 빈칸을 생략한 레벨 순서도 배열 답과 달라요. 5번이 비어 있어도 570은 6번이에요.</p>'
    '<p>처음 배열의 250·610만 지우고 280·580을 17·26번에 남기면 부모가 없는 잘못된 연결이 돼요. 한 자식 삭제로 280은 8번, 580은 13번으로 올라가야 해요. 이 문제는 자식 둘인 대상을 지우지 않으므로 대체 후보를 따로 고를 필요가 없어요.</p>'))
parts.append(layer('retry','해설을 닫고 다시 해 봐요',
    '<ol><li>빈 트리에서 12개 키를 넣으며 각 행에 마지막 부모와 왼쪽·오른쪽을 써요.</li><li>250과 610의 유일한 자식을 확인하고 부모 링크를 직접 고쳐요.</li><li>루트를 1번으로 다시 번호 붙이고, 빈칸을 포함한 배열과 노드 수 10개를 검산해요.</li></ol>'))
parts.append(summary([
    ('떠올릴 개념·공식','<p>서로 다른 키를 받은 순서대로, 작으면 왼쪽·크면 오른쪽의 첫 빈 링크에 넣어요. 배열은 루트 1번, 부모 i의 왼쪽 2i·오른쪽 2i+1이며 i는 키값이 아닌 칸 번호예요.</p>'),
    ('첫 줄','<p>A[1]=520, 다음 490은 520의 왼쪽이어서 A[2]=490이에요.</p>'),
    ('핵심 판단','<p>12개 삽입 뒤 250의 오른쪽 280을 380의 왼쪽에, 이어 610의 왼쪽 580을 570의 오른쪽에 연결해요. 둘 다 한 자식 삭제예요. 280은 8번, 580은 13번으로 옮겨요.</p>'),
    ('배열 답','<p>1:520, 2:490, 3:650, 4:380, 6:570, 8:280, 9:450, 13:580, 18:430, 19:460이에요. 1~30의 나머지는 빈칸이며 앞으로 당기지 않아요.</p>'),
    ('검산','<p>250·610만 없어져 10개예요. 280·580을 보존하고 조상까지 BST 순서를 확인해요. 중위 결과는 280 380 430 450 460 490 520 570 580 650이에요.</p>')]))
(F/'explanations/p2.html').write_text(''.join(parts))


parts=[]
parts.append(layer('understand','낮기만 하면 되는 트리일까요?',
    '<p>20개 키를 모두 쓰면서 최소 높이와 완전이진트리 조건을 동시에 만족해야 해요. 키를 넣는 순서를 조정할 수 있으므로 원하는 자리 모양을 먼저 정한 뒤 키를 배치할 수 있어요.</p>'))
parts.append(layer('recall','이 문제를 봤을 때 떠올릴 개념과 공식',
    '<p>‘높이가 가장 작은’에서는 높이에 들어갈 수 있는 최대 노드 수를 떠올려요. 이 수업에서 높이 $h$는 루트부터 세는 레벨 수예요. 각 층의 최대 노드 수가 $1,2,4,\\ldots$이므로 높이 $h$까지 최대 $2^h-1$개예요. 노드 수 $n\\ge1$이면 $n\\le2^h-1$, 즉 $h\\ge\\lceil\\log_2(n+1)\\rceil$이에요.</p>'
    '<p>‘완전이진트리(complete binary tree)’는 마지막 층 위까지 꽉 차고 마지막 층은 왼쪽부터 채운다는 뜻이에요. 따라서 1번 루트·왼쪽 $2i$·오른쪽 $2i+1$의 배열 표현에서 20개 노드의 모양은 <strong>1~20번 점유</strong>로 먼저 고정돼요. 아무 모양이나 높이만 낮추면 되는 문제가 아니에요.</p>'
    '<p>‘이진 탐색 트리’에서는 왼쪽 전체 &lt; 현재 키 &lt; 오른쪽 전체라는 엄격한 키 조건과 <strong>중위 순회(inorder traversal, LVR)의 오름차순</strong>을 떠올려요. 모양이 고정되어 있을 때 그 모양을 중위 순회하며 작은 키부터 넣으면, 각 서브트리의 왼쪽·현재·오른쪽 순서가 자동으로 맞아요. 단순히 정렬된 키를 배열 1번부터 채우는 방법과는 달라요.</p>'))
parts.append(layer('start','종이에 쓰는 실제 첫 줄',
    '<p>먼저 네 층으로 가능한지 수치로 적어요.</p><p>$$2^4-1=15\\lt20$$</p>'
    '<p>따라서 높이는 최소 5예요. 다음 줄에는 <code>점유할 배열 칸: 1~20</code>이라고 적어 완전이진트리 모양을 고정해요. 이 두 줄을 써야 ‘어느 키를 루트로 고를지’의 기준이 생겨요.</p>'))
arr={int(k):v for k,v in ind['p3']['tree']['sparse_1based_array'].items()}
ordered=[]
def visit(i):
    if i<=20:
        visit(2*i);ordered.append(i);visit(2*i+1)
visit(1)
solve='<h5>1. 자리 20개를 먼저 만들어요</h5><p>1~4층은 $1+2+4+8=15$개로 채워요. 남은 $20-15=5$개는 5층의 왼쪽부터 16·17·18·19·20번 칸에 놓아요. 그러면 높이 5이며 마지막 층의 빈칸은 이 다섯 자리 오른쪽에만 있어요.</p>'
solve+='<h5>2. 루트에 들어갈 값을 판단해요</h5><p>1번 루트의 왼쪽은 2번에서 시작해요. 그 아래 점유 칸은 <code>2, 4, 5, 8, 9, 10, 11, 16, 17, 18, 19, 20</code>으로 12개예요. 오른쪽 3번 가지에는 7개가 들어가요.</p><p>왼쪽에 작은 키 12개를 둬야 하므로 루트는 정렬 순서에서 13번째인 <strong>230</strong>이에요. 작은 키 110~220이 왼쪽, 큰 키 240~300이 오른쪽에 들어가요. 수치 중앙을 기계적으로 고르는 것이 아니라 완전한 모양의 왼쪽 자리 수를 보고 고른 거예요.</p>'
solve+='<h5>3. 고정한 모양의 중위 위치에 작은 키부터 배정해요</h5><p>왼쪽 자리가 있으면 먼저 내려가고, 없으면 그 칸에 다음 작은 키를 써요. 처음에는 <code>1 → 2 → 4 → 8 → 16</code>으로 내려가 16번에 110을 넣어요. 16의 왼쪽·오른쪽은 모두 없으므로 돌아와 8번에 120을 넣고, 8의 오른쪽 17번에 130을 넣어요. 같은 LVR 규칙을 끝까지 반복한 전체 대응이에요.</p>'
solve+=table(['오름차순 차례','중위에서 만난 칸','배정한 키'],[[j,i,arr[i]] for j,i in enumerate(ordered,1)])
solve+='<p>예를 들어 왼쪽 전체를 마치기 전인 8번째에 2번 칸을 만나 180을 넣어요. 13번째에 전체 루트 1번을 만나 230을 넣고, 오른쪽 가지에서도 같은 방식으로 채워 3번 칸은 270이 돼요.</p>'
solve+='<h5>4. 최종 배열을 칸 번호대로 옮겨 적어요</h5>'+array30(arr)
solve+='<p>이 모양을 실제 삽입으로 만들려면 각 부모를 자손보다 먼저 넣으면 돼요. 한 가지 입력 순서는 다음 레벨 순서예요.</p>'+block(seq(ind['p3']['tree']['levelorder']))
solve+='<p>입력 순서가 유일한 것은 아니에요. 같은 목표 트리에서 부모가 모든 자손보다 먼저 나오도록 순서를 정하면 같은 트리가 돼요. 전위 순서도 그 조건을 만족하지만, 문제의 제출 답은 위의 <strong>위치 배열</strong>이에요.</p>'
parts.append(layer('solve','왜 이렇게 푸는지 함께 따라가요',main(solve)))
parts.append(layer('verify','완성 답과 검산',main(
    '<p>정답은 표의 1~20번 값이고 21~30번은 모두 빈칸이에요. 먼저 최소성은 $2^4-1=15\\lt20$으로 높이 4 이하가 불가능하고, 만든 트리가 높이 5를 가지므로 증명돼요. 단지 예시를 하나 만들었다는 이유가 아니라 <strong>불가능한 더 낮은 높이의 상한과 실제 구성</strong>을 함께 확인한 거예요.</p>'
    '<p>완전성은 점유 칸이 정확히 1~20이고 5층의 16~20번만 왼쪽부터 채워졌다는 사실로 확인해요. BST 순서는 각 노드의 왼쪽 부분이 먼저, 노드, 오른쪽 부분이 나중인 중위 위치에 증가하는 키를 넣었으므로 모든 서브트리에서 성립해요. 중위 출력은 정확히 다음과 같아요.</p>'
    +block(seq(ind['p3']['tree']['inorder']))+
    '<p>독립 시뮬레이션에서 위 레벨 순서와 전위 순서를 각각 BST에 삽입했을 때 같은 20칸 배열을 얻었고, 노드 수 20·높이 5·모든 조상 범위도 확인했어요. 순서는 여러 개여도 완전한 20자리 모양에 주어진 오름차순 키를 배정한 최종 배열은 같아요.</p>')))
parts.append(layer('pitfall','가운데 값부터 넣는 것만으로는 부족해요',
    '<p>20개 키의 수치상 가운데인 200이나 210을 무조건 루트로 고르면 왼쪽 12개·오른쪽 7개인 완전 모양에 맞지 않아요. 완전성 없이 높이만 5인 트리는 만들 수 있지만 문제의 두 조건을 모두 만족한 답은 아니에요.</p>'
    '<p>오름차순 키를 입력 순서로 그대로 쓰면 오른쪽으로 긴 경사 트리가 돼요. 오름차순 키를 배열 1번부터 쓰는 것 역시 BST 배치가 아니에요. ‘중위 위치에 키를 배정’, ‘부모부터 삽입’, ‘칸 번호대로 답을 기록’의 세 순서를 구별해요.</p>'))
parts.append(layer('retry','해설을 닫고 다시 해 봐요',
    '<ol><li>20개 노드에 높이 4가 불가능한 이유와 점유 칸 1~20을 적어요.</li><li>루트 왼쪽 자리 12개를 세어 230을 결정한 뒤 중위 위치에 20개 키를 다시 배정해요.</li><li>최종 배열의 빈칸, 중위 오름차순, 높이 5와 마지막 층의 왼쪽 채움을 확인해요.</li></ol>'))
parts.append(summary([
    ('떠올릴 개념·공식','<p>루트 레벨 1인 높이 h에 최대 2^h−1개예요. n≥1이면 h≥⌈log₂(n+1)⌉예요. 완전이진트리는 앞 층이 꽉 차고 마지막 층을 왼쪽부터 채워요. 1번 루트의 왼쪽 2i·오른쪽 2i+1 위치를 중위(LVR)로 읽어 작은 키부터 넣으면 BST 순서가 맞아요.</p>'),
    ('첫 줄','<p>2⁴−1=15&lt;20이므로 최소 높이 5예요. 점유 칸을 1~20으로 먼저 정해요.</p>'),
    ('핵심 판단','<p>왼쪽 12자리·오른쪽 7자리이므로 루트는 13번째 키 230이에요. 2번은 180, 3번은 270이에요. 키를 오름차순으로 적는 위치는 배열 번호순이 아니라 고정 모양의 중위 순서예요.</p>'),
    ('배열과 입력 순서','<p>1~20번: 230 180 270 140 210 250 290 120 160 200 220 240 260 280 300 110 130 150 170 190. 21~30번은 비어요. 이 레벨 순서로 입력하면 만들 수 있어요. 부모가 자손보다 먼저인 다른 순서도 가능하지만 최종 위치 배열은 같아요.</p>'),
    ('검산','<p>높이 4 이하는 15개까지만 가능하고 실제 높이는 5예요. 정확히 1~20번이 차고 마지막 층 16~20번이 왼쪽부터 차요. 모든 20키가 중위 오름차순이고 전체 조상 범위가 맞아요.</p>')]))
(F/'explanations/p3.html').write_text(''.join(parts))


parts=[]
parts.append(layer('understand','대칭으로 만들어야 하는 것은 무엇일까요?',
    '<p>같은 9개 키로 최소 높이의 BST를 만들되, 왼쪽과 오른쪽의 가지 모양이 거울처럼 맞아야 해요. 답에는 그 트리를 실제로 만드는 입력 순서 한 가지를 쓰면 돼요.</p>'))
parts.append(layer('recall','이 문제를 봤을 때 떠올릴 개념과 공식',
    '<p>‘높이가 가장 작은’이라는 단서에서는 높이 $h$에 들어가는 최대 노드 수 $2^h-1$을 떠올려요. $h$는 루트를 1로 세는 레벨 수이고, 노드 수 $n\\ge1$이면 최소 가능한 높이의 하한은 $\\lceil\\log_2(n+1)\\rceil$이에요. 더 낮은 높이가 불가능함을 보인 뒤 그 높이로 구성해야 최소성을 증명할 수 있어요.</p>'
    '<p>‘모양이 좌우대칭’은 왼쪽 서브트리와 오른쪽 서브트리의 모양이 거울 대응(mirror)한다는 뜻이에요. 왼쪽의 왼쪽 가지는 오른쪽의 오른쪽 가지와 대응하고, 빈 링크도 서로 대응해야 해요. 두 쪽의 높이나 노드 수만 같은 조건보다 강해요.</p>'
    '<p>‘이진 탐색 트리’이므로 키는 유일하고 왼쪽 전체는 루트보다 작고 오른쪽 전체는 커야 해요. 대칭은 키값을 같게 복사하는 뜻이 아니에요. 모양을 정한 뒤 중위 순회(inorder traversal, LVR) 자리에 작은 키부터 넣으면 BST 키 조건을 지킬 수 있어요. 원하는 트리를 삽입으로 만들 때는 부모가 자손보다 먼저 나오게 순서를 정해요.</p>'))
parts.append(layer('start','종이에 쓰는 실제 첫 줄',
    '<p>$$2^3-1=7\\lt9$$</p><p>높이 3으로는 부족하므로 최소 높이의 후보는 4예요. 그다음 <code>루트 1개 + 왼쪽 4개 + 오른쪽 4개</code>라고 적어요. 대칭이므로 양쪽 노드 수가 같아야 하고, BST에서 작은 키 4개와 큰 키 4개를 나누는 루트는 5예요.</p>'))
solve='<h5>1. 높이 4인 거울 모양을 정해요</h5><p>루트 5의 왼쪽에는 네 키 1~4, 오른쪽에는 네 키 6~9가 들어가요. 왼쪽 네 자리는 루트·왼쪽·오른쪽을 먼저 두고, 왼쪽 자식의 왼쪽에 한 자리를 더하는 모양으로 정해요. 오른쪽 네 자리는 그것을 뒤집어 오른쪽 자식의 오른쪽에 한 자리를 더해요.</p>'
solve+='<h5>2. 작은 키부터 각 가지 자리에 배정해요</h5><p>왼쪽 모양을 중위로 보면 가장 아래 왼쪽, 그 부모, 왼쪽 전체의 루트, 그 오른쪽 순서예요. 거기에 1·2·3·4를 차례로 놓으므로 왼쪽 루트가 3, 그 자식이 2와 4, 2의 왼쪽이 1이 돼요.</p><p>오른쪽 모양은 그 거울이므로 중위 위치에 6·7·8·9를 넣으면 오른쪽 루트가 7, 그 자식이 6과 8, 8의 오른쪽이 9가 돼요. 이렇게 키 순서와 가지 대칭을 동시에 지켜요.</p>'+treeblock(ind['p4']['tree'])
solve+='<h5>3. 부모를 먼저 넣는 입력 순서를 써요</h5><p>한 층씩 왼쪽부터 읽은 순서를 입력으로 쓰면 모든 부모가 자손보다 먼저 나와요. 그 순서는 다음과 같아요.</p>'+block('5 3 7 2 4 6 8 1 9')
solve+=table(['넣는 키','비교하는 기존 키','붙이는 위치'],[
    [5,'빈 트리','root'],[3,'5','5의 왼쪽'],[7,'5','5의 오른쪽'],
    [2,'5 → 3','3의 왼쪽'],[4,'5 → 3','3의 오른쪽'],
    [6,'5 → 7','7의 왼쪽'],[8,'5 → 7','7의 오른쪽'],
    [1,'5 → 3 → 2','2의 왼쪽'],[9,'5 → 7 → 8','8의 오른쪽']])
solve+='<p>예를 들어 1은 5·3·2보다 모두 작아 왼쪽으로 세 번 내려가요. 9는 5·7·8보다 모두 커 오른쪽으로 세 번 내려가요. 마지막 두 삽입 위치가 서로 거울이 되는 것을 볼 수 있어요.</p><p>이 입력 순서는 한 가지 답이에요. 같은 트리의 전위 순서 <code>5 3 2 1 4 7 6 8 9</code>도 부모가 자손보다 먼저여서 같은 모양을 만들어요. 최소 높이의 대칭 모양 자체도 다른 구성이 가능해요.</p>'
parts.append(layer('solve','왜 이렇게 푸는지 함께 따라가요',main(solve)))
parts.append(layer('verify','완성 답과 검산',main(
    '<p>제출할 수 있는 입력 순서 한 가지는 <code>5 3 7 2 4 6 8 1 9</code>예요. 독립 시뮬레이션에서 이 순서와 위 전위 순서를 각각 삽입해 같은 9개 노드·높이 4의 트리를 얻었어요.</p>'
    '<p><strong>대칭 검산:</strong> 3↔7, 2↔8, 4↔6, 1↔9가 거울 자리예요. 2의 왼쪽 1은 8의 오른쪽 9에 대응하고, 2의 오른쪽 빈칸은 8의 왼쪽 빈칸에 대응해요. 4와 6은 둘 다 단말이며 나머지 빈 링크들도 짝이 맞아요. 따라서 노드 수나 높이만 같다는 확인보다 강한 전체 거울 조건을 만족해요.</p>'
    '<p><strong>BST 검산:</strong> 각 서브트리의 중위 순회 결과를 연결하면 아래처럼 모든 키가 한 번씩 오름차순으로 나와요. 전체 조상 범위 검사도 통과했어요.</p>'+block('1 2 3 4 5 6 7 8 9')+
    '<p><strong>최소 높이 증명:</strong> 높이 3 이하에는 최대 7개이므로 9개를 넣을 수 없어요. 만든 모양의 가장 긴 경로는 <code>5 → 3 → 2 → 1</code> 또는 <code>5 → 7 → 8 → 9</code>로 네 레벨이에요. 하한 4를 달성했으므로 대칭 조건까지 만족하는 최소 높이 답이에요.</p>')))
parts.append(layer('pitfall','같은 높이와 거울 대칭을 구별해요',
    '<p>양쪽의 높이가 같고 노드 수가 같아도 가지 방향이 대응하지 않으면 대칭이 아니에요. 키값을 좌우에 똑같이 쓰는 것도 중복 키와 BST 순서 조건을 깨요.</p>'
    '<p>완전이진트리를 요구한 문제가 아니에요. 완전 모양처럼 마지막 층을 왼쪽에만 채우면 오른쪽에 거울 자리가 없어질 수 있어요. 여기서는 1과 9를 서로 반대 끝에 놓아야 정한 모양의 대칭을 지켜요. 다른 입력 순서나 다른 모양도 가능하지만 높이 4·전체 거울 대칭·BST 순서를 모두 다시 확인해야 해요.</p>'))
parts.append(layer('retry','해설을 닫고 다시 해 봐요',
    '<ol><li>높이 3의 최대 노드 수로 하한을 구하고, 양쪽 네 자리에서 루트 5를 결정해요.</li><li>왼쪽 네 자리 모양 하나와 그 거울을 그린 뒤 중위 순서에 1~9를 넣어요.</li><li>부모를 먼저 넣는 순서를 쓰고, 전체 거울 대응·BST·높이 4를 각각 확인해요.</li></ol>'))
parts.append(summary([
    ('떠올릴 개념·공식','<p>루트 레벨 1인 높이 h에 최대 2^h−1개예요. n≥1에서 h≥⌈log₂(n+1)⌉예요. 좌우대칭은 빈 링크까지 왼쪽·오른쪽 방향이 뒤집혀 대응하는 모양이며, BST는 키가 유일하고 왼쪽 전체 &lt; 현재 키 &lt; 오른쪽 전체예요. 중위(LVR) 자리에 증가하는 키를 넣어요.</p>'),
    ('첫 줄','<p>2³−1=7&lt;9이므로 높이는 적어도 4예요. 1+4+4개로 나누므로 루트는 5예요.</p>'),
    ('핵심 판단','<p>5 아래 3·7, 3 아래 2·4, 7 아래 6·8을 두고 2의 왼쪽 1과 8의 오른쪽 9를 추가해요. 3↔7, 2↔8, 4↔6, 1↔9와 모든 빈 링크가 거울 대응해요. 같은 높이·노드 수만으로는 대칭을 증명하지 못해요.</p>'),
    ('입력 답','<p>5 3 7 2 4 6 8 1 9가 한 가지 답이에요. 부모를 자손보다 먼저 넣는 전위 순서 5 3 2 1 4 7 6 8 9도 가능해요. 입력 순서와 대칭 최소 모양은 유일하지 않고, 완전이진트리 조건은 요구하지 않아요.</p>'),
    ('검산','<p>중위 결과 1 2 3 4 5 6 7 8 9와 전체 조상 범위를 확인해요. 가장 긴 길은 네 레벨이며 높이 3 이하에는 9개가 못 들어가므로 최소 높이 4예요. 다른 답도 키 유일성·전체 거울 모양·최소 높이를 모두 만족해야 해요.</p>')]))
(F/'explanations/p4.html').write_text(''.join(parts))


# Compare authored data with the independently obtained exact states, without
# importing author implementation or treating reference solutions as verification.
comparisons={}
for convention,ak in [('successor','successor_steps'),('predecessor','predecessor_steps')]:
    comparisons['p1_'+convention]=all(s['tree']['sparse_1based_array']==a['array'] for s,a in zip(ind['p1']['conventions'][convention],auth['p1'][ak]))
comparisons['p2_final']=ind['p2']['steps'][-1]['tree']['sparse_1based_array']==auth['p2']['deletions'][-1]['array']
for k in ['p3','p4']:
    comparisons[k+'_array']=ind[k]['tree']['sparse_1based_array']==auth[k]['array']
assert all(comparisons.values())

def find_name(name):
    return next(p for p in REPO.rglob('*') if p.is_file() and unicodedata.normalize('NFC',p.name)==name)

refs=[F/'source.json',F/'evidence/independent-results.json',F/'evidence/answer-data.json',
      F/'evidence/author-p1-p4-hwp-extracted.txt',
      find_name('문제은행.json'),find_name('19-1 중간 복원.txt'),
      find_name('2019-mid.md'),find_name('2018-mid-c024.md'),
      find_name('2018_2_자료구조및알고리즘_중간고사_C024_화B목A (공지용).hwp'),
      REPO/'복습노트/1105/정리노트_1105_Tree.html',REPO/'자료구조_강의록_2026/Software_7_Tree.pdf',
      R/'slides.txt',R/'work/original-2015-ljw-p2.png',R/'work/s7-p24.png',
      REPO/'.agents/skills/ds-problem-explain/SKILL.md',
      REPO/'.agents/skills/ds-problem-explain/references/authoring.md',
      REPO/'.agents/skills/ds-problem-explain/references/verification.md']
report={
    'author':'independent_verifier, now authoring only p1-p4 after completed blind verification',
    'scope':['p1:main','p2:main','p3:main','p4:main'],
    'content':{'status':'pass','evidence':'Seven layers and summary authored per item; original question handled only by assembler. All deletion intermediates and both p1 conventions, p2 12 insert locations + 2 deletions + 30-slot final array, p3 all 20 inorder assignments + array + minimality, p4 mirror construction + 9 insertion steps + minimality are explicit.',
               'items':{k+':main':{'status':'pass','evidence':v} for k,v in {
                 'p1':'Blind exact states match author arrays at every deletion. Both final trees preserve 7 and have 9 unique remaining keys; summary mirrors alternatives and original-candidate cleanup.',
                 'p2':'12 comparison paths and link destinations read from source and matched independent initial relations; deletion intermediate/final arrays match. Final empty slots explicitly retained.',
                 'p3':'Independently fixed complete slots 1..20 and assigned sorted keys in inorder; all 20 placements shown. Height lower bound 5 proved and attained. Different insertion orders distinguished from fixed final array.',
                 'p4':'Independently simulated symmetric 9-node construction. Empty-link mirror pairs, sorted inorder, 4-level height and impossibility below 4 established; multiple answers allowed with same requirements.'}.items()}},
    'source_visual':{'status':'pass','evidence':'p1 original scanned page2 PNG directly viewed: original edges include 6.right=7; handwritten successor/predecessor results match. p2/p3 actual CP949 2019 reconstruction TXT read: exact key order, delete targets and 1..30 array slots match. p4 actual HWP Section0 paragraph text directly decoded from original CFB+raw-deflate: q13 asks same 9 keys, minimum height, mirror shape and input order; no question source figure. No claim of visually rendering HWP or TXT.',
                     'items':{'p1:main':'original-2015-ljw-p2.png viewed; exact deletion order and original 12-node structure confirmed.',
                              'p2:main':'Actual original TXT q10 and transcription q10 compared with full source.json p2.',
                              'p3:main':'Actual original TXT q12 and transcription q12 compared with full source.json p3.',
                              'p4:main':'Actual original HWP q13 text and transcription q13 compared with full source.json p4; source question has no required figure.'}},
    'independent_existing_evidence':{'path':str(F/'evidence/independent-results.json'),'comparison':comparisons},
    'references':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in refs],
    'fragments':[{'path':str(F/f'explanations/p{i}.html'),'sha256':hashlib.sha256((F/f'explanations/p{i}.html').read_bytes()).hexdigest()} for i in range(1,5)],
    'unresolved':[],
    'not_performed':'No build, check, publish or browser review performed by this author task.'}
(R/'work/explain-author-p1-p4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'written':[str(F/f'explanations/p{i}.html') for i in range(1,5)],'report':str(R/'work/explain-author-p1-p4.json'),'comparisons':comparisons,'unresolved':[]},ensure_ascii=False,indent=2))
