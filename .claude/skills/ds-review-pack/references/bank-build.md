# 문제은행 구축 규칙 (`bank` 모드)

문제은행은 `from_the_past/기출/문제은행.json` 한 파일이다. 스키마 검사는 `scripts/bank.py validate`가 한다.

## 원본 표
id와 메타데이터는 이 표로 고정한다(전사 에이전트가 정하지 않는다). `file`은 `from_the_past/기출/` 기준 상대 경로다. 파일명이 NFD일 수 있으니 `os.listdir` + NFC 비교로 찾는다.

| id | file | year | exam | professor | transcribed_from |
|---|---|---|---|---|---|
| `2015-ljw` | `자료구조및알고리즘이해 기출 소스/자료구조및알고리즘 2015기출(이정원).pdf` | 2015 | 미상 | 이정원 | scan |
| `2016-final-ljw` | `자료구조및알고리즘이해 기출 소스/자료구조및알고리즘 기말 (2016이정원)/` (jpg 9장, 파일명 순) | 2016 | 기말 | 이정원 | photo |
| `2017-mid-c050` | `자구알 기출/자료구조및알고리즘_중간고사+(모범답안+공지용).pdf` | 2017 | 중간 | 미상 | text |
| `2017-final-kdh` | `자료구조및알고리즘이해 기출 소스/자료구조및알고리즘_기말고사 (모범답안), 2017 김도희.pdf` | 2017 | 기말 | 김도희 | text |
| `2017-final2` | `자구알 기출/자료구조및알고리즘_기말고사_(공지용_모범답안).pdf` | 2017 | 기말 | 미상 | text |
| `2018-mid-c024` | `자구알 기출/2018_2_자료구조및알고리즘_중간고사_C024_화B목A (공지용).hwp` | 2018 | 중간 | 미상 | hwp |
| `2018-mid-c102` | `자구알 기출/2018_2_자료구조및알고리즘_중간고사_C102_화B목A (공지용).hwp` | 2018 | 중간 | 미상 | hwp |
| `2019-mid` | `자구알 기출/19-1 중간 복원.txt` | 2019 | 중간 | 미상 | txt |
| `2019-final` | `자구알 기출/19-1 기말 복원.hwp` | 2019 | 기말 | 미상 | hwp |
| `2021-mock1` | `자료구조및알고리즘이해 기출 소스/2021학년도 2학기 자료구조및알고리즘이해 기말고사 모의 1회.pdf` | 2021 | 모의 | 미상 | text |
| `unk-final-ltk` | `자료구조및알고리즘이해 기출 소스/자료구조 기말(이태권).pdf` | null | 기말 | 이태권 | text |

- 출제자는 파일명이나 원본 글에 이름이 있을 때만 적는다. 분반 코드 같은 간접 근거로 추측하지 않는다.
- `reviewed`: `text`·`hwp`·`txt`는 `true`, `scan`·`photo`는 `false`. 이전 은행(`RUN/previous-bank.json`)에 같은 id가 `reviewed: true`로 있으면 `true`를 그대로 둔다.
- `has_key`: 전사 에이전트가 원본에 답(모범답안, 괄호 속 답)이 있는지 보고 적는다.

## 정규화 (메인 에이전트, 결과는 `RUN/work/`)
| transcribed_from | 할 일 |
|---|---|
| `txt` | `iconv -f CP949 -t UTF-8 "<원본>" > "$RUN/work/<id>.txt"` |
| `hwp` | `hwp-to-pdf` 스킬로 PDF를 만들어 `$RUN/work/<id>.pdf`에 둔다(스킬이 원본 옆에 쓰면 그 PDF를 `$RUN/work/`로 옮긴다). 그다음 `text`와 같이 한다. 변환에 실패하면 그 원본을 빼고 보고서에 적는다 |
| `text` | 텍스트를 `$RUN/work/<id>.txt`로 뽑고, 쪽 이미지도 만든다(표·그림은 텍스트 추출에서 깨진다) |
| `scan` | 쪽 이미지만 만든다 |
| `photo` | 할 일 없음. jpg 경로 목록을 파일명 순으로 브리프에 넘긴다 |

쪽 이미지·텍스트 추출:
```bash
SRC="<원본 또는 변환된 PDF>" OUT="$RUN/work/<id>" python3 - <<'EOF'
import fitz, os
out = os.environ["OUT"]
os.makedirs(out, exist_ok=True)
doc = fitz.open(os.environ["SRC"])
with open(out + ".txt", "w", encoding="utf-8") as f:
    for i, page in enumerate(doc, 1):
        f.write(f"=== p{i} ===\n{page.get_text()}\n")
        page.get_pixmap(dpi=150).save(os.path.join(out, f"p{i}.png"))
print("쪽", doc.page_count, "→", out)
EOF
```

## 전사 브리프 (원본마다 1명, 병렬, model: opus / lite: sonnet)

---
자구알 기출 원본 `<source-id>`를 전사한다.

- 원본(읽기 전용): `<원본 경로들>` — 쪽 이미지 `<RUN>/work/<source-id>/p*.png`, 텍스트 `<RUN>/work/<source-id>.txt`(있으면), 사진이면 jpg 경로 목록. 이미지는 Read로 직접 본다. 텍스트가 있어도 표·그림·코드 들여쓰기는 이미지로 확인한다.
- 읽기: `<SKILL>/references/bank-build.md`(이 파일 전체)
- 출력: `<RUN>/parts/<source-id>.md`(전사 기록), `<RUN>/parts/<source-id>.json`(문항 조각). 다른 곳에 쓰지 않는다. 임시 파일은 `<RUN>/work/<source-id>/` 아래에만. 저장소(`from_the_past/` 포함)에는 아무것도 쓰지 않는다.
- 전사 기록(.md): 원본 순서대로 `## <번호>번`마다 문제 글을 **원문 그대로**(맞춤법·띄어쓰기도 원문대로, 읽을 수 없는 글자는 `[?]`). 코드는 `c` 펜스, 그림은 `[그림: …]`으로 모양을 글로(트리는 레벨 순서와 부모-자식, 표는 마크다운 표). 원본에 답이 있으면 `**원본 답:**` 줄. 맨 위에 `# <source-id>`와 원본 파일 경로.
- 문항 조각(.json):
  ```json
  {"source": "<source-id>", "has_key": true,
   "problems": [{"id": "<source-id>-q3", "source": "<source-id>", "number": "3", "chapters": [6],
                 "type": "trace", "points": 4, "text": "…", "figure": null,
                 "answer": "…", "answer_origin": "key", "duplicate_of": null}]}
  ```
  - 문항 하나 = 원본의 큰 번호 하나. (a)(b) 같은 하위 문항은 한 문항으로 묶고 `text`에 모두 적는다.
  - `chapters`: 아래 챕터 표로, 풀이에 꼭 필요한 챕터 전부.
  - `type`: `ox`(참/거짓), `blank`(빈칸), `trace`(연산 결과·상태를 구함), `code-read`(코드를 읽고 결과·기능을 답함), `code-write`(코드를 씀), `short`(짧은 서술·정의), `essay`(긴 서술).
  - `points`: 배점 정수, 없으면 `null`. `figure`: 그림이 있으면 한 줄 설명, 없으면 `null`.
  - `text`: 전사 기록의 그 번호 문제 글과 같게(코드는 펜스 포함).
  - `answer`: 원본 답이 있으면 그 답(`answer_origin: "key"`), 없으면 직접 푼 답(`"unverified"` — 메인 에이전트가 검증한다). 그림 답은 글로(레벨 순서, 배열 표현).
  - `duplicate_of`: 항상 `null`(메인 에이전트가 채운다).
- 자기 검사: 원본의 문항 수와 조각 문항 수가 같은지, `python3 -m json.tool <RUN>/parts/<source-id>.json` 통과, `[?]` 개수.
- 보고: 문항 수, `[?]` 개수와 위치, 원본에 답이 있었는지, 챕터를 정하기 어려웠던 문항.
---

## 챕터 표 (강의록 `자료구조_강의록_2026/Software_<N>_*.pdf`)
| N | 강의록 | 다루는 것 |
|---|---|---|
| 1 | `Software_1_자료구조및알고리즘.pdf` | 프로그래밍 언어 분류, 자료구조·알고리즘 개념, 시간복잡도 |
| 2 | `Software_2_Recursion.pdf` | 재귀 |
| 3 | `Software_3_ArrayStructureList.pdf` | 배열, 구조체, 포인터 |
| 4 | `Software_4_List.pdf` | 연결 리스트 |
| 5 | `Software_5_Stack.pdf` | 스택, 수식 표기(후위 표기) |
| 6 | `Software_6_Queue.pdf` | 큐, 원형 큐, 덱 |
| 7 | `Software_7_Tree.pdf` | 트리, 순회, 이진 탐색 트리 |
| 8 | `Software_8_Heap.pdf` | 힙 |
| 9 | `Software_9_Sorting.pdf` | 정렬 |
| 10 | `Software_10_Graph.pdf` | 그래프 |
| 11 | `Software_11_Hash.pdf` | 해싱 |
| 12 | `Software_12_Search.pdf` | 탐색 |

- 이진 탐색 트리는 7, 배열 이진 탐색은 12. 코드의 시간복잡도를 묻는 문제는 1과 그 코드의 자료구조 챕터.
- 표만으로 애매하면 해당 강의록 PDF를 열어 그 개념이 있는 챕터를 고른다.

## 정답 검증 (메인 에이전트)
- 원본마다 `RUN/work/verify_<source-id>.py`를 쓴다. 문항마다 함수 `q<번호>()`가 답 문자열을 돌려주고, 실행하면 `<문항 id>\t<답>`을 한 줄씩 출력한다. 자료구조 연산은 Python으로 그대로 시뮬레이션한다.
- C 코드 문제는 코드를 스크립트 안 문자열로 넣고 `tempfile` 폴더에서 `cc -std=c11 -Wall`로 컴파일·실행한다(저장소로 옮겨도 혼자 돌아가게).
- 판정:
  | 조각의 answer_origin | 실행 결과 | 은행에 쓸 값 |
  |---|---|---|
  | `key` | 같음 | `key` 그대로 |
  | `key` | 다름 | answer = 실행값, `verified`, 보고서 "모범답안과 다른 답" |
  | `unverified` | 같음 | `verified` |
  | `unverified` | 다름 | answer = 실행값, `verified`, 보고서 "에이전트 답과 다른 답" |
  | 실행으로 확인할 수 없음(`essay`, 정의형 `short`·`ox`) | — | `key`면 그대로, 아니면 `unverified` |

## 중복 문항
- 문항 글에 "[2015-1 기출]"처럼 다른 시험을 가리키는 표시가 있거나, 다른 원본 문항과 숫자·코드까지 같으면 `duplicate_of`에 원래 시험 쪽 문항 id를 적는다(원래 시험이 은행에 없으면 `null`로 두고 보고서에 적는다).
- 원 문항 쪽의 `duplicate_of`는 `null`이어야 한다(`bank.py validate`가 검사).
