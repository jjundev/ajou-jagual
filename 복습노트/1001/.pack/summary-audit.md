# 본문–요약 의미 감사

일반·강조·주의·보충의 핵심을 분리해 직접 대조했다. 예시 전체·반복 비유는 압축하며 요약표·예고·링크는 기존 구조를 유지한다.

| 자료·토픽 | 구분 | 본문 핵심 주장 | 실제 대응 요약 문장 | 보완 전 | 판정 / 생략 이유 |
|---|---|---|---|---|---|
| 문제설명_1001_List.html#p1 | 일반 | 역복사이동n-k,최종5원소최선1최악n이다. | 배열 리스트 삽입은 i = length - 1부터 position까지 역방향(i--)으로 복사하며 이동 횟수는 n - k회예요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1001_List.html#p1 | 주의 | 비포화0<=k<=n,순복사는기존값상실한다. | 용량이 충분하고 0≤k≤n이어야 해요. 앞에서 뒤로 복사하면 아직 읽지 않은 30 등이 덮어써져 손실돼요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1001_List.html#p2 | 일반 | 삭제값보관,순복사,n-k-1이동이다. | 삭제는 item을 보관한 뒤 i = position .. length - 2를 순방향(i++)으로 당기며 이동 횟수는 n - k - 1회예요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1001_List.html#p2 | 주의 | 삽입과달리삭제k=n불가,0..n-1이다. | 삭제 유효 위치는 0..length-1이라 position==length는 허용되지 않아요. 삽입의 끝 경계와 구별해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1001_List.html#p3 | 일반 | 삽입삭제교체길이효과와실제추적후조회있다. | 리스트 ADT에서 add는 끼워 넣기(length + 1), delete는 당기기(length - 1), replace는 제자리 값 교체(length 유지)예요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1001_List.html#p3 | 일반 | 순서추적최종AEC길이3,E반환,delete0이동2이다. | get_entry(1) = E, get_length() = 3, delete(0) 시 2개 이동 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1001_List.html#p4 | 일반 | 길이정의와주소전달원본/복사비용이유있다. | 유효 원소는 0 .. length - 1로만 정의되며, 원본 구조체 수정과 복사 비용 절감을 위해 ArrayListType *L(&L)을 전달해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1001_List.html#p4 | 일반 | empty/full과경계2정상3오류있다. | 직후 length = 0, is_empty = 1, is_full = 0, []; length == 3일 때 is_empty = 0, is_full = 1, get_entry(&L, 2) 정상 반환, get_entry(&L, 3) 위치 오류 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1001_List.html#p5 | 일반 | 링크순서/연결순서/선행노드조건/비용있다. | 연결 리스트는 head에서 link를 따라 순서를 읽으며, 삽입은 new_node->link = p->link 후 p->link = new_node 순서로 연결해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1001_List.html#p5 | 일반 | 탐색과추가링크공간비용있다. | 선행 노드 알 때 삽입·삭제 $O(1)$이나 추가 링크 공간 및 탐색 $O(n)$ 소요 | pass | pass / 기존 충족, 수정 없음 |
| 복습문제_1001_List.html | 구조 | 문제·보기·힌트·풀이·정답을 보존하고 기존 요약 없음 확인 | — | pass | pass / .sum 없는 복습문제는 S 추가 대상 아님 |
| 정리노트_1001_List.html#s0-list | 일반 | 순서가달라지면다른리스트로집합과다르다. | 리스트는 항목의 자리까지 의미가 있는 모임이에요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1001_List.html#s0-adt | 일반 | 객체연산계약은구현과별개다. | ADT는 저장 방법과 별개로 객체와 연산의 약속을 정해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1001_List.html#s0-adt | 일반 | 주요연산계약정의가요약에서빠졌다. | add_first·add_last·add는 추가, delete·clear는 일부·전체 제거, replace는 값 교체예요. is_in_list는 포함, get_entry는 위치값, get_length는 길이, is_empty·is_full은 상태 검사, display는 전체 표시예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1001_List.html#s0-example | 일반 | 추가는자리생성,삭제빈칸제거,교체값만변경이다. | 추가는 자리를 만들고, 삭제는 빈자리를 없애며, 대치는 값만 바꿔요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1001_List.html#s0-example | 조건 | 위치는0부터이고replace는길이유지다. | 위치는 0부터 세고 삽입은 기존 값을 없애지 않아요. replace는 해당 위치 값만 바꾸므로 길이가 그대로예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1001_List.html#s1-choice | 일반 | 배열인덱스접근단순하지만삽입삭제최악On이다. | 배열은 접근이 간단하지만 중간 삽입과 삭제에서 원소를 옮겨요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1001_List.html#s1-choice | 구분 | 연결위치알때만링크변경이며탐색비용별도,구현위험이다. | 연결 리스트는 위치를 이미 알면 링크 변경만 하지만 찾는 비용은 별도이며, 잘못 연결하면 뒤쪽 데이터에 도달하지 못해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1001_List.html#s1-struct | 일반 | 배열과논리길이를묶는상태다. | ArrayListType은 배열과 현재 원소 수를 함께 저장해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1001_List.html#s1-struct | 조건 | init길이0,유효0..length-1,empty/full조건이다. | init은 배열을 지우지 않고 length=0으로 만들며 유효 범위는 0..length-1이에요. is_empty는 length==0, is_full은 length==MAX_LIST_SIZE일 때 1을 반환해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1001_List.html#s1-insert | 일반 | 뒤에서부터복사하고새값저장한다. | 배열 삽입은 뒤에서부터 옮긴 뒤 새 값을 써요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1001_List.html#s1-insert | 조건 | 비포화와위치0..length허용,마지막부터복사후길이증가다. | 가득 차지 않고 0≤position≤length일 때 i=length-1부터 position까지 list[i+1]=list[i]로 역복사한 뒤 값을 쓰고 length를 늘려요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1001_List.html#s1-delete | 일반 | 삭제뒤원소전방당김최악On이다. | 배열 삭제는 뒤의 원소를 앞으로 당겨 빈칸을 없애요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1001_List.html#s1-delete | 조건 | 유효0..length-1,삭제값저장후순복사길이감소반환이다. | 0≤position<length를 검사하고 삭제값을 item에 보관해요. i=position..length-2에서 list[i]=list[i+1]로 당긴 뒤 length를 줄이고 item을 반환해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1001_List.html#s2-node | 일반 | 노드링크로논리순서와물리배치분리된다. | 헤드 포인터에서 시작해 노드의 링크 필드를 따라가면 물리적 위치와 관계없이 논리적 순서를 읽어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1001_List.html#s2-node | 일반 | 빈헤드NULL,헤드는노드밖별도변수이며노드동적할당이다. | 헤드 포인터는 노드 일부가 아닌 별도 변수이며 빈 리스트에서는 NULL이에요. 노드는 필요할 때 malloc으로 만들어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1001_List.html#s2-kinds | 일반 | 단순마지막NULL,원형첫노드,이중앞뒤링크이다. | 세 연결 리스트는 노드가 잇는 방향과 마지막 링크가 가리키는 곳이 달라요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1001_List.html#s2-kinds | 주의 | 단순NULL은링크필드이지데이터가아니다. | 단순 리스트의 마지막 NULL은 데이터가 아니라 링크 필드 값이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1001_List.html#s2-insert | 일반 | 새노드기존뒤연결후앞링크변경으로안전보존한다. | 새 노드가 기존 다음 노드를 먼저 가리키고, 앞 노드가 새 노드를 가리키게 해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1001_List.html#s2-insert | 조건 | 빈L별도헤드교체;위치알때O1탐색별도이다. | 빈 리스트 L==NULL이면 L=new로 헤드를 정해요. 위치를 이미 아는 링크 대입만 O(1)이고 위치 탐색은 별도예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1001_List.html#s3-cheatsheet | 구조 | 기존요약·예고·링크화면유지 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_1001_List.html#s3-next | 구조 | 기존요약·예고·링크화면유지 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_1001_List.html#s3-links | 구조 | 기존요약·예고·링크화면유지 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
