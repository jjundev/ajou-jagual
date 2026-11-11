# 소스코드 분석

## 제공 함수

<table>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>void init_memory_list(void);</td>
<td>인자: 리스트 포인터. 반환값: 없음. 변경 상태: 리스트 초기화. 표준 출력 원문에 초기 블록이 나타난다. MemoryBlock 의 prev/next 가 head 에 연결되고 free 블록이 전체 크기로 들어선다. 외부 단편화는 발생하지 않는다. MSVC 경고도 없다. 관찰한 메모리 지도에서 하나의 FREE 블록이 확인된다. 이 과정에서 정의되지 않은 동작은 없다. 추가 함수는 만들지 않았다.</td>
</tr>
<tr>
<td>MemoryBlock *insert_block_after(void);</td>
<td>인자: 리스트 포인터와 기준 블록. 반환값: 새 블록 포인터. 변경 상태: 새 블록 삽입. 실제 결과는 리스트 길이가 1 증가한다. Best-Fit 과 달리 First-Fit 이므로 탐색은 첫 FREE 에서 멈춘다. O(n) 시간이 필요하다. 검증했다. 하네스에서 head 기준 삽입이 지켜진다. 주어진 함수 형식을 유지한다.</td>
</tr>
</table>

## 구현 대상 함수

<table>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int allocate_memory(void);</td>
<td>인자: 리스트 포인터와 pid, size. 반환값: 성공 1 실패 0. 변경 상태: FREE 블록을 PID 블록으로 치환. 하네스에서 ALLOC 명령이 들어오면 First-Fit 으로 탐색한다. 실제 결과는 메모리 지도에 반영된다. 관찰한 할당 순서는 명령 순서와 같다. 외부 단편화 수치도 함께 기록된다. 주어진 함수 형식을 유지한다.</td>
</tr>
<tr>
<td>void release_memory(void);</td>
<td>인자: 리스트 포인터와 pid. 반환값: 없음. 변경 상태: PID 블록을 FREE 로 전환 뒤 인접 FREE 를 병합. 실제 결과는 두 블록이 하나로 합쳐진다. O(n) 시간이 걸린다. 관찰한 메모리 지도에서 병합이 즉시 반영된다. 검증했다. 하네스에서 RELEASE 명령으로 호출된다.</td>
</tr>
</table>

![터미널의 실제 실행 화면. 명령별 처리 결과와 메모리 지도를 보여 준다.](https://example.com/img01.png)

![터미널의 실제 실행 화면. 명령별 처리 결과와 메모리 지도를 보여 준다.](https://example.com/img02.png)

![터미널의 실제 실행 화면. 명령별 처리 결과와 메모리 지도를 보여 준다.](https://example.com/img03.png)

**실제 출력**

```plain text
hw2-author-evidence-naa1l07t % clear; ./run 03
프로세스의 수를 입력하세요. (1~8): 자원의 종류의 개수를 입력하세요. (0~5):
Need matrix:
EXIT_STATUS: 0
```
