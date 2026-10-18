# 강의노트 기반 문제(`lecture-code`) 본문 구조화·경량화 및 문제설명 패널 서식 개선 — 설계

## Intent
10개 복습팩(`0907`–`1015`)의 `data-source-kind="lecture-code"` 문항 47개에 대해:
1. **우측(문제) 패널 서식 부재 해결**: `문제설명_<range>_<slug>.html`의 문제 패널(`.problem-pane`)에서 `lecture-code` 문항이 조건과 질문 구분 없이 줄글로 이어지는 문제를 해결한다. `mpe_source.py`에서 `lecture-code` 문항을 `conditions_html`(배지 + 전제 조건 + 코드/표 블록)과 `ask_html`(번호 목록 질문)로 분리하여 `<h4>구할 것</h4>` 영역에 렌더링하고, `pdf_lecture.py`도 구조화된 `<ol>` 질문 블록과 선행 조건 블록을 일관되게 분리하도록 맞춘다.
2. **문제 본문(`.problem`) 및 해설 프래그먼트(`fragments/pN.html`) 경량화·서식화**: 한 문단에 조건·C 선언·부수 질문 4~7개가 줄글로 뭉쳐 있는 47개 `lecture-code` 카드의 `.problem`을 **배지(`<p><span class="badge">강의 예제 기반 자체 출제</span> Sx py</p>`) + 간결한 전제 조건(`<p>` 및 필요 시 `<pre><code class="language-c">`) + 핵심 소문항 2~3개(`<ol><li>(a) …</li><li>(b) …</li></ol>`)**로 재작성하고 모든 C 식별자·수식·상수에 인라인 `<code>`를 적용한다. 아울러 `fragments/pN.html`의 `understand`(원문 통짜 복사 제거 → 1~2문장 요약)와 `solve`·`verify`(`data-subpart` 분리 및 정답 줄글 중복 제거)도 함께 정돈한다.

분류: architectural — `ds-problem-explain`(`mpe_source.py`, `note-template.html`, `port-provenance.json`) + `ds-review-pack`(`pdf_lecture.py`, `card-rules.md`) 파서·렌더러 연동 및 10개 복습팩 47문항 개정·재발행.

## 확정 결정
| # | 결정 항목 | 선택값 | 근거 |
|---|---|---|---|
| 1 | `lecture-code` `.problem` 마크업 구조 | `<p>`(배지) + `<p>`/`<pre><code>`(전제·초기 상태) + `<ol><li>(a) …</li><li>(b) …</li></ol>`(핵심 소문항) | `mpe_source.subparts` 계약 준수 및 조건/질문 시각적 분리 |
| 2 | 문제 패널 `conditions` vs `ask` 분리 방식 | `mpe_source.split_statement(statement_html, source)`에서 `lecture-` 카드의 질문 `<ol>`(또는 질문 문장)을 `ask_html`로 분리하고 배지·전제·코드를 `conditions_html`에 유지 | `mpe_render.py`가 `ask_html` 존재 시 자동으로 `<h4>구할 것</h4>`을 렌더링하며 `check_artifacts`의 원문 보존 검사와 호환됨 |
| 3 | PDF 생성기(`pdf_lecture.split_lecture_problem`) 연동 | `<ol>`/`<ul>` 질문 블록이 있을 때 선행 `<p>` 블록은 `cond`로, `<ol>`/`<ul>` 블록은 `<ol class="ds-asks">`로 분리 | 기존 `pdf_lecture.py:56`이 `<ol>` 존재 시 조건까지 통째로 `ask`에 넣던 폴백 동작을 개선해 문제/답안 PDF 품질 유지 |
| 4 | `fragments/pN.html` 해설 경량화 | `understand`는 1~2문장 핵심 요약으로 작성(문제 원문 복붙 금지), `solve`·`verify`는 `data-subpart="a"`, `"b"` 단위로 구조화하고 정답 통짜 복붙 제거 | `authoring.md` 원칙 및 `mpe_contract.validate_fragment` 소문항 계약 준수 |
| 5 | 문제 본문 경량화 수준 | 카드당 핵심 소문항 2~3개(`(a)`~`(c)`)로 압축·통합하되, `manifest.json`의 `terms`와 핵심 학습 목표(`objectives`)는 100% 보존 | 과밀한 줄글(최대 1,374자)을 줄여 문제 파악 속도와 가독성을 높임 |
| 6 | 적용 대상 범위 | 10개 복습팩(`0907`, `0914`, `0917`, `0921`, `0928`, `1001`, `1005`, `1008`, `1012`, `1015`)의 `lecture-code` 47문항 전체 + 파생 산출물(HTML/MD/문제설명/PDF) 일괄 재생성 | 전 주차 복습노트 일관성 확보 |
| 7 | 배지 옆 슬라이드 출처 표기 | `.problem` 첫 문단은 `<p><span class="badge">강의 예제 기반 자체 출제</span> Sx py</p>`로 대표 슬라이드만 표기하고, `추가 근거 p…`는 `details.original`("강의 예제 보기") 안으로 일원화 | 문제 패널 첫 줄의 불필요한 페이지 번호 나열 제거 (`check_html.BADGE_LEAD_RE` 및 `pdf_lecture.CITATION`과 100% 호환) |

## 대상 문항 (10개 팩 47문항)
| 팩 | 문항 ID (`source_kind="lecture-code"`) | 개수 |
|---|---|---|
| `0907` | `p4`, `p5`, `p6`, `p7` | 4 |
| `0914` | `p6`, `p7`, `p8` | 3 |
| `0917` | `p5`, `p6` | 2 |
| `0921` | `p5`, `p6`, `p7`, `p8`, `p9`, `p10`, `p11` | 7 |
| `0928` | `p5`, `p6`, `p7`, `p8`, `p9` | 5 |
| `1001` | `p1`, `p2`, `p3`, `p4`, `p5` | 5 |
| `1005` | `p3`, `p4`, `p5`, `p6`, `p7`, `p8`, `p9`, `p10`, `p11` | 9 |
| `1008` | `p2`, `p3`, `p4`, `p5` | 4 |
| `1012` | `p7`, `p8`, `p9` | 3 |
| `1015` | `p4`, `p5`, `p6`, `p7`, `p8` | 5 |

## 제외 범위
- 기출(`past-exam`) 및 교과서(`textbook`) 카드 — 원문 보존 계약에 따라 수정하지 않는다.
- 정리노트(`정리노트_*.html`), STT 녹취록, 강의록 원본 PDF, 교과서 JSON 원본은 수정하지 않는다.
