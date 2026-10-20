# 본문–요약 의미 감사

일반·강조·주의·보충의 핵심을 분리해 직접 대조했다. 예시 전체·반복 비유는 압축하며 요약표·예고·링크는 기존 구조를 유지한다.

| 자료·토픽 | 구분 | 본문 핵심 주장 | 실제 대응 요약 문장 | 보완 전 | 판정 / 생략 이유 |
|---|---|---|---|---|---|
| 문제설명_1005_List.html#p1 | 일반 | 다음링크검사해D에서정지한다. | 다음 링크 검사 → 마지막 D에서 정지 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p1 | 조건 | 비어있지않은전제,p자체NULL조건아니다. | 비어 있지 않은 리스트에서 p->link!=NULL을 검사하므로 마지막 D에 남아요. head==NULL에는 p->link 역참조를 적용할 수 없어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1005_List.html#p2 | 일반 | head부터NULL직전까지하나씩센다. | head부터 p!=NULL 동안 한 노드당 +1 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p2 | 주의 | 비순환전제,빈0,마지막포함,입력n그대로안쓴다. | 비순환 단순 리스트를 실제로 순회해 마지막 노드까지 세고 빈 리스트는 0이에요. 입력 n을 그대로 반환하지 않고, p->link!=NULL로 마지막을 빼먹지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1005_List.html#p3 | 일반 | 꼬리B연결결과ABCD,빈head1반환head2,잘못p조건NULL오류있다. | 마지막 노드에서 멈추려면 while (p->link != NULL)로 이동한 뒤 p->link = head2를 대입해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p3 | 주의 | 노드서로미공유전제,정렬병합아니다. | 두 입력은 노드를 공유하지 않는 단순 리스트라는 전제이며, concat은 정렬 병합이 아닌 순서 그대로의 이어 붙이기예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1005_List.html#p4 | 일반 | 세포인터단계결과와다음주소보존/빈NULL있다. | r = q; q = p; p = p->link;로 포인터를 먼저 한 칸씩 전진시킨 뒤 q->link = r;로 링크를 뒤집어요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p4 | 주의 | 반환값호출자가받아야head갱신된다. | 호출자의 head가 자동으로 바뀌지 않으므로 head=reverse(head)로 반환된 새 첫 노드를 받아야 해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1005_List.html#p5 | 일반 | 공백/앞/중간3가지결과와이중포인터이유있다. | (a) 공백: N -> NULL, p == NULL: N -> A -> B -> NULL, p == A: A -> N -> B -> NULL (b) 순서 역전 시 B 유실, 호출자 head 변경을 위해 ListNode **phead 사용 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p5 | 주의 | pNULL은빈리스트아니다. | p==NULL은 리스트 공백이 아니라 선행 노드가 없어 맨 앞에 넣는다는 뜻이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1005_List.html#p6 | 일반 | 우회후해제,첫삭제별도와단일NULL이다. | 선행 노드 p(또는 *phead)의 링크를 removed->link로 먼저 우회시킨 뒤 free(removed)를 호출해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p6 | 일반 | 해제먼저읽으면해제메모리접근이다. | free 선행 시 해제 메모리 접근 오류 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p7 | 일반 | 꼬리head의역할,first/last한줄차이,양끝O1이다. | 원형 리스트에서 head가 꼬리를 가리키면 첫 노드는 head->link이므로 양끝 삽입이 모두 $O(1)$이에요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p8 | 일반 | 새양링크후오른쪽뒤왼쪽갱신,삭제두대입있다. | 새 노드의 llink, rlink를 먼저 정한 뒤 before->rlink->llink = new_node 후 before->rlink = new_node 순서로 갱신해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p8 | 일반 | 순서역전N자기llink,B미갱신이다. | 순서 역전 시 N->llink = N이 되고 B->llink 미갱신 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p9 | 일반 | 재귀출력순/NULL기저/남은노드감소/검색노드주소/원본보존이다. | 재귀 방문은 p->data 출력 후 p->link로 호출해 NULL에서 멈추고, search는 일치 노드의 주소(ListNode *) 또는 NULL을 반환해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p9 | 일반 | 원본유지빈결과와종료이다. | 지역 p만 이동해 원본 유지, 공백 시 무출력·NULL 반환, 남은 노드 수 감소로 유한 종료 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p10 | 일반 | 헤드노드없음NULL,센티널공백자기링크이다. | 헤드 노드 없는 공백은 head = NULL, 헤드 노드 H가 있는 이중 원형 공백은 H->llink = H, H->rlink = H예요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p10 | 구분 | 비공백H양링크첫끝,길이증감갱신필요다. | 헤드 포인터는 주소 변수이고 H는 데이터 없는 노드예요. 비공백 H->rlink는 첫 노드·H->llink는 마지막 노드이며, 저장된 length는 삽입·삭제 때 갱신해야 해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1005_List.html#p11 | 일반 | 지수큰쪽소비,같으면합둘다소비,잔여보존/0미저장있다. | 높은 지수 항을 먼저 결과에 붙이고 해당 포인터를 전진시키며, 지수가 같으면 계수를 더하고 p, q를 함께 전진시켜요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1005_List.html#p11 | 조건 | 결과꼬리유지로추가O1전제에서m+n이다. | O(m+n)은 결과 리스트의 마지막 포인터를 유지해 항 추가가 O(1)이라는 조건에서 성립해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 복습문제_1005_List.html | 구조 | 문제·보기·힌트·풀이·정답을 보존하고 기존 요약 없음 확인 | — | pass | pass / .sum 없는 복습문제는 S 추가 대상 아님 |
| 정리노트_1005_List.html#s0-insert-order | 일반 | 새후속연결후선행링크변경으로뒷부분보존한다. | 새 노드의 링크를 먼저 after에 잇고, 그다음에 선행 노드의 링크를 새 노드로 바꿔요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s0-insert-order | 조건 | 빈L새헤드,before링크로after알아별도after불필요다. | 빈 L은 L=new로 정하고, 일반 삽입은 before의 링크로 after를 알 수 있어 선행 노드만 받아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s0-remove-pseudo | 일반 | 선행우회후destroy해제이다. | 선행 노드의 링크가 removed 다음 노드를 가리키게 바꾼 뒤 removed의 메모리를 반납해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s0-node-impl | 일반 | 자체참조데이터링크노드동적할당과헤드다. | 노드는 링크가 자기 타입을 가리키는 구조체이고, malloc으로 하나씩 만들어 링크로 이어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s0-node-impl | 일반 | data와link초기화,p1link=p2로연결한다. | ListNode 크기로 할당해 data와 link를 채우고 p1->link=p2로 이어요. 여러 포인터가 같은 노드를 가리켜도 돼요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s0-insert-node | 일반 | 헤드수정위해주소이중포인터,새링크먼저다. | 헤드 포인터가 바뀔 수 있어서 그 주소를 이중 포인터로 받고, 세 경우 모두 새 노드의 링크부터 이어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s0-insert-node | 구분 | 빈헤드,선행NULL,일반삽입구분이다. | *phead==NULL은 공백으로 new_node->link=NULL 뒤 헤드를 갱신해요. p==NULL은 비어 있음이 아닌 맨 앞 삽입이며, 그 외는 p 뒤에 넣어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s0-insert-node | 보충 | 호출인자&head매개phead로밖변수바꾸는예제는보충이다. | 보충 호출 예제: insert_node(&head,NULL,&b)의 phead는 &head를 복사받아 *phead로 호출자의 head를 바꿔요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s0-remove-node | 일반 | 선행NULL헤드다음,그외우회후free이다. | p가 NULL이면 헤드를 한 칸 옮기고, 아니면 선행 노드의 링크를 removed 다음으로 바꾼 뒤 free해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s0-remove-node | 일반 | 변경대상head자신주소이중포인터다. | *phead=(*phead)->link는 호출자 head를 다음 노드로 옮겨요. head 자체를 고치므로 자신의 주소를 이중 포인터로 받아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s1-display | 일반 | 임시p로순회하여NULL종료,On이다. | 임시 포인터 p를 한 칸씩 옮기며 NULL을 만날 때까지 출력해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s1-display | 조건 | 재귀는출력후link호출,남은노드감소,head변경안한다. | 재귀 버전은 현재 data 출력 뒤 p->link로 호출해 남은 노드 수를 줄이고 NULL에서 멈춰요. 지역 p만 옮겨 호출자의 head는 유지해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s1-search | 일반 | 일치노드포인터반환실패NULL,최악On이다. | 값이 맞는 노드를 만나면 그 노드를, 끝까지 없으면 NULL을 돌려줘요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s1-concat | 일반 | head1꼬리에head2연결,첫길이기준On이다. | head1의 끝 노드를 찾아 그 링크를 head2에 이어 주면 합병돼요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s1-concat | 조건 | 빈한쪽처리및반환head1,link조건다. | head1이 NULL이면 head2, head2가 NULL이면 head1을 반환해요. 둘 다 있으면 p->link==NULL에서 멈춰 head2를 잇고 head1을 반환해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s1-reverse | 일반 | pqr로노드안옮기고링크반전한다. | p, q, r을 한 칸씩 밀며 각 노드의 링크를 앞 노드 쪽으로 돌려 역순 리스트를 만들어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s1-reverse | 보충 | 다음주소보존전링크수정금지,반환값수신필요,빈NULLOn은보충이다. | 보충(수업에서 유도하지 않음): r=q; q=p; p=p->link; 뒤 q->link=r로 뒤집어 다음 주소를 보존해요. head=reverse(head)로 새 헤드를 받고, 빈 입력은 NULL·시간은 O(n)이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s2-circular | 일반 | 꼬리head와headlink첫노드로양끝상수접근이다. | 헤드 포인터가 마지막 노드를 가리키면 머리와 꼬리를 모두 바로 찾아요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s2-circular | 구분 | 꼬리head는필수규칙아닌채택구현이고원형은모든노드순회가능다. | 마지막 링크가 첫 노드를 가리켜 어느 노드에서든 전체로 돌아갈 수 있어요. head를 꼬리에 두는 것은 필수 규칙이 아닌 이 구현의 트릭이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s2-insert-first | 일반 | 새→첫,꼬리→새,비공백head유지다. | 새 노드가 첫 노드를 먼저 가리키고, 꼬리의 링크를 새 노드로 바꿔요. 헤드는 그대로예요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s2-insert-first | 조건 | 빈때만헤드변경자기링크다. | 공백일 때는 *phead=node와 node->link=node로 노드 하나의 고리를 만들어요. 헤드 유지는 비공백 분기의 설명이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s2-insert-last | 일반 | first연결후새꼬리로head이동한다. | 맨 앞에 넣는 두 줄 뒤에 헤드를 새 노드로 옮기면 맨 뒤 삽입이 돼요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s2-insert-last | 조건 | 빈자기고리이고head이동은연결이후다. | 공백은 새 노드를 헤드로 두고 자기 자신에 연결해요. 비공백은 node->link=옛 첫 노드, 옛 꼬리->link=node 뒤 *phead=node로 새 꼬리를 정해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s3-dlist | 일반 | 앞뒤링크와데이터없는헤드노드/포인터구분이다. | 노드마다 llink와 rlink 두 링크로 앞뒤를 모두 가리키고, 데이터 없는 헤드 노드가 리스트의 처음과 끝을 잡아요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s3-dlist | 조건 | 빈헤드양링크자기,비공백첫끝,공간구현비용증가다. | 공백 헤드 노드의 두 링크는 자기 자신이고, 비공백에서는 rlink가 첫 노드·llink가 마지막 노드예요. 양방향 탐색 대신 링크 공간과 코드 복잡도가 늘어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s3-dinsert | 일반 | 새두링크먼저3후4순서필수다. | new_node의 두 링크를 먼저 잇고, 3번을 4번보다 먼저 실행해야 after의 llink를 제대로 고쳐요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s3-dinsert | 주의 | 1,2교환가능;4선행은Nllink자기화이다. | 1·2는 바꿔도 되지만 before->rlink->llink=new_node 뒤 before->rlink=new_node 순서는 지켜요. 거꾸로 하면 새 노드 llink가 자기 자신을 가리켜요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s3-dremove | 일반 | 헤드보호,양옆링크우회후free이다. | removed의 양옆 노드가 서로를 가리키게 두 링크를 고친 뒤 free하고, 헤드 노드는 지우지 않아요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s3-dremove | 구분 | 노드llink로선행알아탐색필요없고void반환이다. | removed의 llink·rlink로 양옆을 알아 선행 탐색이 필요 없어요. 헤드일 때는 void 함수의 return;으로 값 없이 끝내요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s4-poly | 일반 | 지수비교같으면합,큰쪽붙임과결과있다. | 두 다항식 리스트를 최고차항부터 비교하며 지수가 같으면 계수를 더하고, 다르면 큰 쪽 항을 C에 붙여요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s4-poly | 일반 | 합0제외둘다전진,큰한쪽전진,남은꼬리보존다. | 같으면 합 0은 빼되 p,q 모두 전진하고, 다르면 큰 지수 쪽만 전진해요. 한쪽이 끝나면 남은 항들을 모두 C에 가져와요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s4-poly | 보충 | m+n시간은수업에서따로말안한보충이다. | 보충(수업에서 복잡도는 따로 말하지 않음): 각 항을 한 번씩 소비하므로 항 수 m,n에 대해 O(m+n)이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s4-listtype | 일반 | head,length저장으로길이O1이다. | ListType은 헤드 포인터와 노드 개수 length를 함께 들고 있어서 길이를 바로 돌려줄 수 있어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s4-listtype | 일반 | 길이는삽입삭제갱신,empty는headNULL,위치→포인터변환재사용이다. | is_empty는 head==NULL을 검사하고 length는 삽입·삭제 때 증감해 실제 노드 수와 맞춰요. 위치 기반 ADT 연산은 노드 포인터 기반 함수를 재사용해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s4-add-delete | 일반 | 선행위치변환후기존함수재사용한다. | add와 delete는 get_node_at으로 선행 노드를 구한 뒤 이미 있는 insert_node와 remove_node를 재사용해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1005_List.html#s4-add-delete | 조건 | 삽입0..length,삭제비공백0..length-1,pos-1음수NULL이다. | 삽입은 0≤position≤length, 삭제는 비공백에서 0≤pos<length예요. get_node_at(pos-1)에서 음수는 NULL이라 맨 앞 분기를 선택해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s4-add-delete | 보충 | 복잡도보충은get_node_at순회에기인한다. | 보충(수업에서 복잡도는 따로 말하지 않음): get_node_at이 링크를 따라가므로 위치 기반 add·delete는 O(n)이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1005_List.html#s5-cheatsheet | 구조 | 기존요약·예고·링크구조유지 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_1005_List.html#s5-next | 구조 | 기존요약·예고·링크구조유지 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_1005_List.html#s5-links | 구조 | 기존요약·예고·링크구조유지 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |

## 기존 본문의 별도 결함

`정리노트_1005_List.html#s4-add-delete`의 `remove_node(&(list->head),p,(p!=NULL)?p->link:NULL)`는 pos=0에서 p=NULL·removed=NULL을 넘긴다. head는 다음으로 이동하지만 free(NULL)은 첫 노드를 해제하지 않으므로 누수가 남는다. 이는 작업 전부터 있던 본문 코드의 결함이다. 바인딩 계약에 따라 본문을 보존하고, 본문에 없는 추론을 요약에 추가하지 않았다. 별도 범위 수정이 필요하다.
