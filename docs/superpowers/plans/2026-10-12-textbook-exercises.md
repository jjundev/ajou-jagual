# 교과서 연습문제 JSON 추출 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 교과서 1~14장 전체 연습문제를 원문 JSON과 직접 재제작한 SVG 그림·표로 제공한다.

**Architecture:** 생명과학 웹과제 추출의 출처·관찰 분리와 검토 해시 원칙을 참고해 교과서 전용 계약을 만든다. 페이지별 인벤토리를 먼저 작성하고 문항 및 자산 구조를 전사한 뒤 SVG를 렌더링한다. 후보의 자동 검증과 전체 시각 대조를 마친 후 장별 JSON 14개를 마지막에 확정한다.

**Tech Stack:** Python 3.10+, PyMuPDF, jsonschema Draft 2020-12, pytest, standard-library XML/HTML/hash/path utilities, SVG, HTML/CSS, 실제 브라우저 검수.

**Spec:** `docs/superpowers/specs/2026-10-12-textbook-exercises-design.md`. 실행자는 계획과 설계를 모두 읽는다.

## Global Constraints

- 입력은 `교과서/origin`의 1~14장 PDF 전체이며 현재 기준 14개, 44쪽이다. 실행 시작 때 실제 목록·쪽수·SHA256을 다시 확인한다.
- 실제 파일명 Unicode를 보존한다. NFC는 검색 비교에만 사용한다.
- 큰 문항 하나를 한 question으로 저장한다. `id`는 `ch05-q06`처럼 장과 문항 번호를 최소 두 자리로 표현하고 `number`는 원문 문자열을 보존한다.
- `content`는 순서 있는 text/code/figure/table/subquestions 블록이다. `options`도 원문 label과 순서 있는 content를 지원한다.
- 코드·수식·원문의 오타를 보존한다. 필요하면 원문과 분리된 `issues`에 오류를 설명한다.
- `answer`는 null이다. 직접 정답·해설을 작성하지 않는다.
- 문제용 SVG와 대체 설명에는 원본에 없는 정답 힌트를 추가하지 않는다.
- SVG는 직접 그린 도형·선·화살표·텍스트만 사용한다. 원본 크롭·이미지 삽입·외부 링크·스크립트를 금지한다.
- 표는 행·열·셀 데이터와 새 SVG를 함께 제공한다. 인쇄된 빈칸과 병합 셀을 유지한다.
- PDF 쪽번호는 1부터 시작하며 책 쪽번호는 직접 읽은 경우만 숫자로 저장하고, 확인할 수 없으면 null이다.
- 검토 상태는 pending/verified/blocked이다. verified에는 실제 원본 대조 기록과 현재 payload SHA256이 필요하다.
- 최종 문항·보기·소문항·그림·표 수는 페이지별 인벤토리와 일치해야 한다. 숫자는 전사를 마친 뒤 집계하며 미리 추정하지 않는다.
- 임시 전체 페이지 렌더링·전사 초안·후보는 `tmp/textbook-exercises/<run-id>/`에 둔다.
- 기존 원본·기출은행·복습 스킬·기존 보고서를 변경하지 않는다. 기존 산출물이 있으면 덮어쓰지 않는다.
- 실제 구현 전에 작업 격리와 원본 접근을 using-git-worktrees로 점검한다. 현재 origin은 untracked이므로 새 worktree에 자동 포함된다고 가정하지 않는다. 원본 바이트 동일 사본 또는 명시적 읽기 경로를 준비한다.
- 커밋·푸시는 별도 사용자 요청 없이는 실행하지 않는다. 각 Task의 commit은 승인된 경우에만 해당 Task의 정확한 파일 목록으로 수행한다.

## Review Focus

1. NFD/NFC 이름과 정규화 충돌: 원래 이름을 유지하고 두 이름이 충돌하면 선택을 추측하지 않는다. root 밖 경로·symlink는 거부한다 — Tasks 1–2.
2. 페이지 경계의 문제·코드·표: 같은 큰 문항의 모든 페이지를 연결하고 누락된 continuation을 거부한다 — Tasks 1, 2, 4.
3. C 문자열의 `\\n`, `<`, `&` 및 손글씨 정답 표시: 코드는 그대로 보존하고 필기는 관찰로만 저장한다 — Tasks 2, 4, 5.
4. 오른쪽 자식만 있는 트리, 방향/병렬 간선, 표 빈칸/병합 셀: 연결·좌우·방향·값을 바꾸지 않는 SVG를 만든다 — Task 3.
5. 검토 이후 source/model/SVG 변경과 기존 경로·중간 게시 실패: 검토 재사용과 덮어쓰기를 거부하고 이번 실행 소유 파일만 정리한다 — Tasks 2, 5, 6.

---

## 파일 구조와 작업 경계

이하 `B`는 실제 NFD 이름으로 탐색한 교과서 폴더, `S=B/제작자료`, `T=S/tests`, `R=tmp/textbook-exercises/<run-id>`, `P=R/package`이다. 문서의 NFC 경로는 설명용이며 코드에서는 실제 경로를 찾는다. 각 CLI는 경로를 따옴표로 감싸 전달한다.

| 파일 | 책임 |
|---|---|
| `S/scripts/requirements.txt` | 실행·검증 의존성 PyMuPDF/jsonschema/pytest |
| `S/scripts/source.py` | Unicode 경로 해석, 원본 인벤토리·바이트 해시·검토용 페이지 렌더링 |
| `S/question-bank.schema.json` | 각 장별 JSON 형식과 메모리 내 합본 계약 |
| `S/scripts/model.py` | 스키마·블록·검토 payload 계약, 기본 구조 검증 |
| `S/scripts/assets.py` | 구조 모델을 새 SVG로 렌더링하고 SVG 허용 형식 검사 |
| `S/scripts/validate.py` | 출처·인벤토리·모델·자산·검토 해시·완성도 검사와 CLI |
| `S/scripts/preview.py` | 전체 문제·보기·소문항·SVG·표·출처 HTML 미리보기 |
| `S/scripts/publish.py` | 최종 경로 충돌 검사, 배포 사본·독점 생성·실패 정리 |
| `T/conftest.py`, `test_source.py`, `test_model.py`, `test_assets.py`, `test_delivery.py` | synthetic 계약·회귀·실패 검증 |
| `R/chapters/chNN.json`, `R/transcripts/chNN.md`, `R/pages/chNN-pNN.png` | 장별 전사와 전체 페이지 검토 자료 |
| `P/origin/*.pdf` | 실제 원본과 바이트 동일한 후보 검증용 로컬 사본; 최종 배포에서는 제외 |
| `P/[NN]_*_연습문제.json`, `P/assets/*.svg` | 검증 전 후보와 직접 그린 자산 |
| `P/제작자료/inventory.json`, `asset-models.json`, `preview.html`, `verification.md` | 배포할 데이터·미리보기·검수 기록 |
| `B/[NN]_*_연습문제.json`, `B/assets/*.svg`, `S/inventory.json`, `asset-models.json`, `preview.html`, `verification.md` | 검증 완료 후 최종 배포 |

신규 스킬 등록과 기존 은행 통합은 하지 않는다. JSON과 SVG가 주 산출물이며 도구는 반복 검증에 필요한 범위만 구현한다.

## 고정 데이터 인터페이스

`Bank`, `Inventory`, `AssetModel`, `ChapterPart`는 JSON 호환 `dict[str, object]`이다. 함수 시그니처에서는 이 별칭을 `model.py`에 정의하고 다른 파일에서 import한다. dict의 실제 필드는 아래 계약과 schema로 고정한다.

- Bank: `schema_version=1`, `sources`, `chapters`, `questions`, `assets`.
- Source: `id=s01`, `path=origin/<실제 파일명>`, `sha256`, `page_count`; Chapter: `id=ch01`, `number=1`, `title`, `source_ids`.
- Question: `id`, `chapter_id`, `number`(양의 정수 숫자 문자열), `kind`(choice/short/trace/code-read/code-write/essay/mixed), `content`, `options`, `source_refs`, `answer=null`, `printed_answer=null 또는 {content,source_refs}`, `observations`, `issues`, `review`.
- SourceRef: `source_id`, `pdf_page`(1-based), `book_page`(int 또는 null). Question·Asset·인쇄 답의 위치 모두 이 형식을 사용한다.
- text block: `{type:"text",text}`; code: `{type:"code",language:"c" 또는 "text",text}`; figure/table: `{type:"figure" 또는 "table",asset_id}`; subquestions: `{type:"subquestions",items:[{id,label,content}]}`. Option: `{label,content}`. 모든 content는 같은 Block 목록이며 빈 목록·빈 label을 허용하지 않는다. 그림이 들어간 보기도 그대로 표현한다.
- Review: `{status:"pending"|"verified"|"blocked",payload_sha256:null 또는 hex64,notes:[{locator,text}]}`. Issue: `{kind:"unreadable"|"figure-incomplete"|"source-error"|"external-context",description,source_refs,blocking:bool}`. 읽기·그림 불완전은 blocking=true다. 완전히 읽힌 인쇄 오타와 외부 본문 참조는 원문을 보존하고 blocking=false로 기록할 수 있다.
- Observation: `{kind:"handwriting"|"selection-mark"|"other",description,source_refs}`. 출력의 문제 content와 분리한다.
- Inventory: `{schema_version:1,sources,pages:[{source_id,pdf_page,book_page,occurrences:[{question_id,number,role:"start"|"continuation",option_labels,subquestion_labels,asset_ids}],review}]}`. 옵션·소문항 label 목록은 해당 페이지에서 관찰한 순서이며 continuation을 따라 합쳐 원문 순서를 확인한다. 번호 점프는 누락을 숨기지 않고 페이지 review.notes에 설명한다.
- Asset: `{id,path:"assets/<id>.svg",sha256,model_id,alt,source_refs,review}`. Model 파일: `{schema_version:1,models:[AssetModel]}`; Model에는 `id`, `kind`, `data`, `layout`가 있다. `kind`는 tree/graph/array/table/vector다. `layout`은 좌표·크기·색이며 문항 내용인 `data`를 대신하지 않는다.
- tree.data: `{nodes:[{id,label,left:null 또는 id,right:null 또는 id}],root}`; graph.data: `{nodes:[{id,label}],edges:[{id,from,to,directed:bool,label,weight:null 또는 string}]}`; array.data: `{cells:[{index:int,value:string}],pointers:[{label,index:int}]}`. 빈칸 value는 `""`이며 생략하지 않는다.
- table.data: `{rows:int,cols:int,cells:[{row:int,col:int,text:string,rowspan:int,colspan:int,header:bool}]}`. 좌표는 0-based, 병합 셀은 시작점만 기록하고 나머지 좌표를 covered로 판정한다. 모든 셀 위치가 정확히 한 셀에 포함돼야 한다.
- vector.data: `{entities:[{id,label,meaning}],primitives:[...]}`. 임의 그림도 사람이 분석한 엔티티 설명과 허용 SVG 도형의 속성만 기록한다. PNG/JPEG/data URI를 primitive로 허용하지 않는다.
- ChapterPart: `{chapter,questions,assets,models}`. Inventory는 ChapterPart로부터 생성하지 않고 원본을 별도로 보며 기록한다.
- `question_payload(bank, question, book_dir, inventory, models)`는 question에서 review를 뺀 내용, question과 printed_answer가 참조한 출처의 현재 파일 해시, 해당 페이지 occurrence/review, 재귀적으로 참조한 asset 각각의 asset_payload를 포함한다. `asset_payload(bank,asset,book_dir,models)`는 review 제외 asset, 현재 source/SVG 해시, 해당 model 전체를 포함한다. inventory page payload는 review 제외 페이지 기록과 source 현재 해시다. canonical SHA256은 UTF-8 JSON의 sort_keys=True, ensure_ascii=False, separators=(",",":")다.

### Task 1: 원본 인벤토리와 전체 페이지 검토 기반

**Files:** Create `S/scripts/source.py`, `requirements.txt`, `T/conftest.py`, `T/test_source.py`; generate `R/pages/`, `P/origin/`, `P/제작자료/inventory.json` 초안.

**Interfaces:**
- Consumes: 실제 `B/origin` PDF와 읽기 전용 생명과학 참고 스킬.
- Produces: `resolve_local(base: Path, relative: str) -> Path`, `file_sha256(path: Path) -> str`, `inspect_sources(origin: Path) -> list[dict]`, `prepare_run(origin: Path, run: Path) -> Path`. prepare_run 반환값은 P이며 원본 바이트 동일 사본·전체 페이지 PNG·pending inventory를 만든다. inspect_sources는 01~14의 유일한 PDF 14개를 요구하고 실제 filename으로 Source를 만든다.

- [x] **Step 1: 개발 환경 준비.** 기존 Python3의 PyMuPDF 유무를 확인하고 `python3 -m venv R/venv`, `R/venv/bin/python -m pip install -r S/scripts/requirements.txt`로 독립 실행 환경을 만든다. requirements는 PyMuPDF/jsonschema/pytest 세 패키지다. 모든 Run의 `PY`는 이 Python 절대경로다. 세 모듈 import 성공과 Python>=3.10을 확인한다.
- [x] **Step 2: 실패 테스트 작성.** test_source.py에 `test_nfd_path_returns_actual_filename`, `test_normalized_collision_raises`, `test_parent_escape_and_symlink_escape_raise`, `test_missing_duplicate_chapter_raise`, `test_prepare_run_keeps_source_bytes_and_renders_every_page`를 추가한다. 아래 synthetic PDF fixture는 conftest.py에서 fitz로 만든다. Unicode 충돌이 파일시스템에서 표현되지 않으면 iterdir 반환 목록을 주입해 두 entry를 재현한다.

```python
def test_prepare_run_keeps_source_bytes_and_renders_every_page(source_dir, tmp_path):
    before = {p.name: p.read_bytes() for p in source_dir.glob("*.pdf")}
    package = prepare_run(source_dir, tmp_path / "run")
    assert {p.name: p.read_bytes() for p in source_dir.glob("*.pdf")} == before
    assert {p.name: p.read_bytes() for p in (package / "origin").glob("*.pdf")} == before
    inv = json.loads((package / "제작자료/inventory.json").read_text())
    assert len(inv["sources"]) == 14
    assert len(inv["pages"]) == sum(s["page_count"] for s in inv["sources"])
    assert all(p["review"]["status"] == "pending" for p in inv["pages"])
```

- [x] **Step 3: 실패 확인.** Run `PY -m pytest T/test_source.py -q`; source API 미존재로 FAIL이어야 한다.
- [x] **Step 4: source.py 구현.** 정확한 파일명을 보존하고 NFC 비교 충돌을 거부한다. PDF를 읽어 전체 페이지를 200dpi로 렌더링하며 읽기 어려운 쪽은 실행자가 더 높은 해상도로 재검토할 수 있게 원본 위치를 남긴다. 각 source byte hash와 실제 쪽수를 저장한다. 정규화·root 외부 symlink를 추측으로 처리하지 않는다.
- [x] **Step 5: 통과 및 실제 입력 점검.** Run `PY -m pytest T/test_source.py -q`; PASS. inspect_sources의 실제 결과가 페이지 수 `[2,5,2,3,3,5,2,5,3,3,2,5,2,2]`, 합 44인지 확인한다. 다르면 입력 변경 기록을 남기고 기존 완료 수치를 재사용하지 않는다.
- [x] **Step 6: 변경 검토.** `git diff --check`; 승인된 경우 Task 파일만 `feat(textbook): inventory exercise source pages`로 커밋한다. 원본과 기존 tmp 자료는 stage하지 않는다.

### Task 2: 혼합 문항 계약과 검토·완성도 검증

**Files:** Create `S/question-bank.schema.json`, `S/scripts/model.py`, `S/scripts/validate.py`, `T/test_model.py`.

**Interfaces:**
- Consumes: Task 1의 resolve_local/file_sha256, 고정 데이터 인터페이스.
- Produces: `canonical_digest(value: object) -> str`, `validate_structure(bank: Bank) -> list[str]`, `validate_chapter_part(part: ChapterPart) -> list[str]`, `question_payload(bank: Bank, question: dict, book_dir: Path, inventory: Inventory, models: dict) -> dict`, `asset_payload(bank: Bank, asset: dict, book_dir: Path, models: dict) -> dict`, `page_payload(page: dict, sources: list[dict], book_dir: Path) -> dict`, `validate_bank(bank: Bank, book_dir: Path, inventory: Inventory, models: dict, *, complete: bool = False) -> list[str]`, `main(argv: list[str] | None = None) -> int`.
- CLI: `PY S/scripts/validate.py P --complete`. book_dir는 지정한 교과서 폴더이며 inventory/model은 그 안의 `제작자료/`에서 읽는다. 성공은 exit 0과 `PASS chapters=14 sources=14 pages=44 questions=N assets=M`, 실패는 exit 1과 ID/위치가 포함된 오류다. 작은 synthetic bank는 `--complete` 없이 검사한다.

- [x] **Step 1: 실패 테스트 작성.** 유효 mixed bank fixture를 만들고 `test_recursive_content_and_option_figure`, `test_answer_must_be_null`, `test_text_code_json_roundtrip`, `test_question_spans_two_pages`, `test_missing_continuation_page_blocks_complete`, `test_duplicate_question_and_unknown_refs`, `test_pending_or_blocking_issue_rejected`, `test_changed_source_model_or_svg_invalidates_review`를 작성한다. 유효 상태를 만든 뒤 각 dependency를 하나씩 바꿔 stale 검토가 거부되는지 확인한다.

```python
def test_text_code_json_roundtrip(valid_bank):
    code = 'printf("%d\\n", n); if (n < 1 && p != NULL) return 0;'
    valid_bank["questions"][0]["content"] = [{"type": "code", "language": "c", "text": code}]
    restored = json.loads(json.dumps(valid_bank, ensure_ascii=False))
    assert restored["questions"][0]["content"][0]["text"] == code
    assert validate_structure(restored) == []
```

- [x] **Step 2: 실패 확인.** Run `PY -m pytest T/test_model.py -q`; 신규 API 미존재로 FAIL.
- [x] **Step 3: 계약·기본 검증 구현.** model.py에 JSON 별칭과 위 payload API를 구현하고 schema에서 additionalProperties=false와 재귀 Block을 정의한다. `$defs.chapterPart`를 추가하고 validate_chapter_part는 같은 schema의 해당 정의를 사용한다. printed_answer도 출처를 필수로 갖는다. observations는 원문 content에 자동 삽입하지 않는다. 생명과학 코드에 런타임 import를 걸지 않는다.
- [x] **Step 4: validate.py 구현.** 구조·ID·참조·실제 파일 해시·review digest·인벤토리 occurrence를 검사한다. complete는 모든 원본·페이지·문항·자산 verified, start occurrence 정확히 하나, 번호 집합 일치, continuation 포함, 옵션·소문항 순서와 자산 집합 일치, blocking issue 0을 요구한다. 실제 14장 범위와 sources/page 수를 검사한다. 원문 오류 및 필요한 본문 참조는 완전히 전사한 경우 공개하고 허용한다. 검토된 실제 source가 초기 hash와 다르면 실패한다. 생명과학 원본 코드 해시와 참고 범위를 `S/verification.md` 작성 때 기록하도록 주석에 명시한다.
- [x] **Step 5: 통과 확인.** Run `PY -m pytest T/test_source.py T/test_model.py -q`; 전부 PASS. source만 changed인 사례에서도 초기 stored hash와 현재 hash 불일치가 반드시 검출돼야 한다.
- [x] **Step 6: 변경 검토.** `git diff --check`; 승인된 경우 Task 파일만 `feat(textbook): validate mixed exercise bank and review hashes`로 커밋한다.

### Task 3: 그림·표 구조 모델과 새 SVG 렌더링

**Files:** Create `S/scripts/assets.py`, `T/test_assets.py`; Modify `S/scripts/validate.py`의 asset 검증 부분.

**Interfaces:**
- Consumes: AssetModel 계약과 XML 표준 라이브러리.
- Produces: `validate_model(model: AssetModel) -> list[str]`, `render_svg(model: AssetModel, alt: str) -> str`, `validate_svg(text: str) -> list[str]`, `svg_payload_text(text: str) -> list[str]`, `main(argv: list[str] | None = None) -> int`. CLI `PY S/scripts/assets.py --models P/제작자료/asset-models.json --bank P --output P/assets`는 asset별 model/alt를 찾아 SVG를 생성한다. 생성 뒤 pending asset.sha256만 갱신하며 verified 상태/검토 해시는 자동 부여하지 않는다.

- [x] **Step 1: 실패 테스트 작성.** `test_right_only_child_preserves_slot`, `test_directed_parallel_edges_and_loop`, `test_array_empty_slots_and_pointer_index`, `test_table_empty_merged_cells_and_full_coverage`, `test_overlapping_or_missing_table_cells_rejected`, `test_labels_are_xml_escaped`, `test_vector_forbids_embedded_image`, `test_svg_rejects_script_image_href_external_url`를 작성한다. SVG XML의 노드 id/label, edge id/방향 primitive, table cell 좌표를 구조 데이터와 비교한다. 좌표 fixture는 primitive geometry 관계를 assert하며 이미지 스냅샷 byte 비교로 대체하지 않는다.

```python
def test_table_empty_merged_cells_and_full_coverage(table_model):
    assert validate_model(table_model) == []
    svg = render_svg(table_model, "원문의 표")
    assert validate_svg(svg) == []
    assert svg_payload_text(svg) == [c["text"] for c in table_model["data"]["cells"] if c["text"]]
    assert len(ET.fromstring(svg).findall('.//{http://www.w3.org/2000/svg}rect')) == len(table_model["data"]["cells"])
```

- [x] **Step 2: 실패 확인.** Run `PY -m pytest T/test_assets.py -q`; 렌더러 API 미존재로 FAIL.
- [x] **Step 3: assets.py 구현.** data의 노드·edge id는 SVG id로 보존하고 array/table cell id는 좌표로부터 생성한다. layout 좌표를 직접 작성할 수 있게 하고 좌우 자식·방향·값을 data로 검증한다. tree의 순환/중복 부모·없는 root, graph 없는 endpoint, array pointer 범위, 표 병합 overlap/missing을 거부한다. 화살표는 선·polygon으로 직접 그린다. SVG tag/attribute 허용 목록은 생명과학 svg.py의 안전한 도형 범위를 참고하되 source 파일에 참조를 적는다. vector primitives에도 같은 검사 적용. svg_payload_text는 도형에 표시되는 text/tspan만 문서 순서대로 반환하고 title/desc는 제외한다.
- [x] **Step 4: 자산과 검토 연결.** validate.py가 모든 참조 SVG의 안전 형식·model 유효성·render_svg 결과와 파일 바이트 일치·현재 asset hash를 검사하게 한다. figure/table 블록과 model.kind가 맞는지 확인한다. XML 검사 PASS는 시각/의미 대조 PASS와 별개다.
- [x] **Step 5: 통과 확인.** Run `PY -m pytest T/test_assets.py T/test_model.py -q`; 전부 PASS. synthetic 모델 5종을 브라우저로 렌더링해 화살표·라벨·빈칸·병합 테두리를 확인한다.
- [x] **Step 6: 변경 검토.** `git diff --check`; 승인된 경우 Task 파일만 `feat(textbook): redraw figures and tables from structured models`로 커밋한다.

### Task 4: 전체 14장 전사와 재제작 자산의 원본 대조

**Files:** Create `R/transcripts/ch01.md`~`ch14.md`, `R/chapters/ch01.json`~`ch14.json`, `P/[NN]_*_연습문제.json`, `P/제작자료/asset-models.json`, `P/assets/*.svg`; Update `P/제작자료/inventory.json`.

**Interfaces:**
- Consumes: Tasks 1–3의 source refs/contract/render/validation, 전체 페이지 PNG와 실제 PDF.
- Produces: 완전히 대조한 ChapterPart 14개, 메모리 내 Bank, Inventory, model 파일, 신규 SVG. 장별 자료는 장별 파일을 메모리에서 합치기 전에 validate_chapter_part로 검사한다.

- [x] **Step 1: 1~7장 페이지 인벤토리 작성.** 22쪽을 순서대로 직접 읽고 시작·continuation, 보기·소문항·자산·책 쪽번호를 기록한다. 책 쪽번호가 보이지 않으면 null로 두고 notes에 이유를 적는다. 각 페이지를 확인한 후 page_payload digest와 실제 대조 notes로 review를 채운다.
- [x] **Step 2: 1~7장 원문 전사.** 발문·조건·보기·코드·소문항·인쇄 답·본문 참조를 ch01~ch07에 기록하고 transcripts와 JSON의 원문을 비교한다. 선택 동그라미·손글씨는 observations에만 기록한다. 오류를 고쳐서 문제 본문에 넣지 않는다. code는 language=c/text 구분과 원래 escape를 확인한다.
- [x] **Step 3: 1~7장 그림·표 재제작.** 각 Asset에 source_refs를 기록하고 model_id로 asset-models의 data/layout을 연결한 뒤 assets CLI로 렌더링한다. 문제 단서의 포인터·빈칸·배열 인덱스·병합 표를 원본과 SVG의 동일 위치 관계로 대조한다. model과 SVG 둘 다 검토하고 기록한다.
- [x] **Step 4: 1~7장 검증.** 인벤토리 대비 번호/옵션/소문항/자산 순서와 page refs가 일치하고 unreadable/figure-incomplete가 0인지 확인한다. 실제 원문 대조가 끝난 asset부터 digest를 기록하고 question 검토를 마지막에 기록한다. 미해결이면 candidate 상태로 남기고 위치를 보고하며 이후 독립 장의 작업은 계속한다.
- [x] **Step 5: 8~14장 페이지 인벤토리 작성.** 나머지 22쪽에 Step 1과 동일한 관찰·continuation 규칙을 적용한다. 트리의 필기와 인쇄 라벨을 구분한다. 정렬의 페이지 상단 이어지는 표/코드도 이전 문제에 연결한다.
- [x] **Step 6: 8~14장 원문 전사.** ch08~ch14에서 트리·힙·그래프·정렬·탐색·해싱의 보기와 코드·표를 모두 보존한다. 문제에서 요구한 결과 그림을 원본 제공 그림으로 새로 만들지 않는다. 외부 본문 알고리즘 참조는 원문 그대로 남긴다.
- [x] **Step 7: 8~14장 그림·표 재제작.** 좌우 자식·노드 라벨·간선 endpoint/방향/가중치·루프·표 값·빈칸을 models에 기록하고 렌더링한다. 원문에 없는 노드/순회번호/정답 표시를 SVG·alt에 추가하지 않는다.
- [x] **Step 8: 8~14장 검증.** Step 4의 대조·review 순서·미해결 처리 규칙을 적용한다. 인벤토리와 구조 모델을 읽으며 SVG를 별도로 확인한다.
- [x] **Step 9: 장별 후보 작성과 메모리 내 합본 검증.** sources/chapters는 장 순서, questions는 장·원문 큰 번호 순서로 정렬하고 문제 내부 순서는 그대로 유지한다. 모델·자산 ID 중복을 거부한다. 모든 원문 큰 번호를 보존하며 번호 점프를 임의 보완하지 않는다. source-error는 바꾸지 않고 issues에 남긴다.
- [x] **Step 10: 후보 자동 검증.** Run `PY S/scripts/validate.py P --complete`; 14 sources/14 chapters/44 pages, 인벤토리에서 집계된 N questions/M assets, 오류 0이면 PASS. 실패 시 candidate를 보존하고 blocking issue 및 notes의 위치를 보고한다. 검증을 통과하려고 notes/hash만 덮어쓰지 않는다.
- [x] **Step 11: 데이터 검토.** 장별 문항·보기·소문항·그림·표 수를 verification 초안에 기록한다. 완료 데이터의 커밋은 Task 6 발행 후에만 수행하고 R/P 후보는 stage하지 않는다.

### Task 5: 미리보기와 충돌 없는 배포

**Files:** Create `S/scripts/preview.py`, `S/scripts/publish.py`, `T/test_delivery.py`; generate `P/제작자료/preview.html`, `P/제작자료/verification.md` 초안.

**Interfaces:**
- Consumes: validate_bank, candidate package, asset SVG/model/table data.
- Produces: `render_preview(bank: Bank, book_dir: Path, models: dict) -> str`, `publish_package(package_dir: Path, destination: Path) -> list[Path]`, 두 파일의 `main(argv: list[str] | None = None) -> int`.
- Preview CLI: `PY S/scripts/preview.py P`.
- Publish CLI: `PY S/scripts/publish.py --package P --destination B`; 미리보기 visual 검토가 있는 현재 verification manifest와 모든 dependency hash, 실제 destination/origin 동일 hash를 요구한다. 최종 JSON과 payload 파일만 확정하고 origin 사본·tmp·scripts/tests는 배포하지 않는다.

- [x] **Step 1: 실패 테스트 작성.** `test_preview_preserves_block_and_option_order`, `test_code_and_html_are_text_not_markup`, `test_table_and_figure_in_options`, `test_preview_source_links_relative_to_materials_dir`, `test_publish_needs_current_browser_review`, `test_existing_json_or_asset_preserved`, `test_partial_publish_failure_removes_only_owned_files`, `test_source_modified_in_destination_blocks_publish`, `test_json_is_created_last`를 추가한다. 2번째 exclusive create에서 오류를 주입해 기존 unrelated 파일 bytes 동일, 새 정본 JSON 부재, 이미 새로 만든 파일만 정리됐음을 assert한다.

```python
def test_code_and_html_are_text_not_markup(valid_bank, package):
    text = '<script>alert(1)</script> printf("\\n"); &'
    valid_bank["questions"][0]["content"] = [{"type": "code", "language": "c", "text": text}]
    html = render_preview(valid_bank, package, {"schema_version": 1, "models": []})
    assert "&lt;script&gt;" in html
    assert '<script>alert(1)</script>' not in html
    assert 'printf("\\n");' in unescape(html)
```

- [x] **Step 2: 실패 확인.** Run `PY -m pytest T/test_delivery.py -q`; preview/publish API 미존재로 FAIL.
- [x] **Step 3: preview.py 구현.** 원문 번호와 모든 블록을 순서대로 표시한다. text/code/label은 HTML escape하고 SVG는 검증한 자산만 embed한다. 각 문제에 source PDF 및 페이지/책 쪽번호를 표시한다. source 링크는 preview가 제작자료 안에 있으므로 `../origin/...` 기준으로 만든다. 그림 src는 `../assets/...`다. 경로는 실제 상대 경로를 URL encode하고 HTML attribute escape해 공백·한글 이름을 보존한다. 코드와 넓은 표는 내부 스크롤, SVG는 viewBox와 max-width:100%를 사용한다. tables는 셀 데이터로 접근 가능한 HTML 표도 제공한다. observation/printed_answer/issues는 별도 접힌 기록으로 두고 원문 발문에 섞지 않는다.
- [x] **Step 4: publish.py 구현.** 후보를 complete 검증한 후 manifest의 원문대조·모든 자산 visual review·browser review와 dependency hashes를 재검증한다. manifest 형식은 `{schema_version:1,package_sha256,origin_sha256,content_review:{status,notes},asset_reviews:[{id,sha256,status,notes}],browser_reviews:[{viewport,theme,status,notes}],counts,unresolved}`이며 검토 상태는 verified/pending/blocked다. package_sha256는 manifest 자체를 제외한 장별 JSON·preview·inventory·models·SVG의 경로/해시 목록 digest다. source counts는 같은 목록이 아닌 실제 bank/inventory로 다시 집계한다. 단순 위조 방지 장치라고 주장하지 말고 실제 검토 기록과 해시 일치를 검사한다. 전용 배포 사본을 destination과 같은 filesystem에 준비하고 os.link의 독점 생성으로 assets/data/preview/verification을 먼저, 장별 JSON 14개를 마지막에 만든다. 어떤 기존 destination 파일도 덮어쓰지 않는다. 실패 정리는 이번 실행이 만든 inode가 현재 경로 inode와 같은 경우에만 수행한다.
- [x] **Step 5: 통과 확인.** Run `PY -m pytest T/test_delivery.py -q`; 전부 PASS. 실제 candidate preview를 생성하고 asset/source 링크 해석을 확인한다. 아직 실제 발행하지 않는다.
- [x] **Step 6: 변경 검토.** `git diff --check`; 승인된 경우 Task 파일만 `feat(textbook): preview and publish verified exercise artifacts`로 커밋한다.

### Task 6: 전체 대조·브라우저 검수·최종 산출물 확정

**Files:** Finalize `P/제작자료/verification.md`, `P/제작자료/verification.json`; Publish `B/[NN]_*_연습문제.json`, `B/assets/*.svg`, `S/inventory.json`, `asset-models.json`, `preview.html`, `verification.md`, `verification.json`.

**Interfaces:**
- Consumes: Tasks 1–5의 후보·검증 도구·미리보기·publisher.
- Produces: 검증 완료 장별 JSON 14개/SVG와 읽을 수 있는 검수 기록. 최종 답에는 실제 생성 파일, 장별/총 문항·자산 수, 판독/원본 결함, 직접 답을 작성하지 않았음을 보고한다.

- [x] **Step 1: 전체 도구 테스트.** Run `PY -m pytest T -q`; 전부 PASS. 실패가 생기면 해당 책임 Task의 코드·회귀 사례만 고친다. source/model/SVG 바꾸기 regression 및 실패 rollback을 포함해야 한다.
- [x] **Step 2: 44쪽 두 번째 대조.** 최초 전사 순서와 달리 큰 문항 단위로 PDF→JSON을 대조한다. 모든 코드·보기·소문항과 관련 페이지를 확인하고 인벤토리, JSON, model, SVG의 연결이 맞는지 기록한다. 최초 전사와 같은 사람이 확인하면 두 번째 대조라고 기록하고 독립 검토라고 표현하지 않는다.
- [x] **Step 3: 모든 자산 시각 검수.** 각 SVG를 원본 전체 페이지와 비교해 빠진 노드·값·빈칸·좌우·방향·연결·텍스트·표 셀이 없는지 확인한다. 검토 notes와 현재 SVG 해시를 asset_reviews에 저장한다. 문항별 확인 완료 후 question review를 갱신한다.
- [x] **Step 4: 후보 브라우저 검수.** 로컬 HTTP server로 P를 제공한다. 실제 브라우저의 1280×900·375×812, light/dark 네 조합에서 전체 문항 수와 모든 자산의 표시, 글자·선 겹침, 문서 가로 넘침 0, 코드/표 내부 스크롤, source 링크, console/resource 오류 0을 확인한다. 서버는 검토가 끝나면 종료한다. screenshots/console evidence는 R에 저장하고 최종 verification에는 위치와 관찰 결과를 기록한다.
- [x] **Step 5: 현재 내용으로 검수 기록 확정.** verification.md에는 각 장 문항/보기/소문항/그림/표 수, source hash, 참고 스킬 파일 hash, 자동검증·시각 검토 범위, unresolved와 source-error 목록을 적는다. 동일 파일 basename의 verification.json은 Task 5 manifest 계약으로 저장한다. 후보 변경 시 영향을 받은 실제 검토를 다시 하고 hash를 기록한다.
- [x] **Step 6: 최종 후보 검사.** Run `PY S/scripts/validate.py P --complete`; 오류 0과 실제 집계된 총 수가 맞아야 한다. manifest의 content/asset/browser 상태는 모두 verified, blocking unresolved는 0이어야 한다. 원본 SHA256이 처음과 같고 모든 최종 목적 파일이 아직 없는지 검사한다.
- [x] **Step 7: 최종 파일 발행.** Run `PY S/scripts/publish.py --package P --destination B`; exit 0과 생성 경로 목록을 확인한다. 원본 사본은 배포하지 않는다. 기존 파일 충돌이 있으면 candidate를 남기고 conflict 경로를 보고하며 덮어쓰지 않는다.
- [x] **Step 8: 발행 후 확인.** Run `PY S/scripts/validate.py B --complete`; PASS. 최종 preview를 실제 브라우저에서 한 번 열어 상대 링크/자산이 후보와 같이 동작하는지 확인한다. 최종 JSON/SVG/model/inventory/preview 해시가 후보와 동일한지 비교한다. `git diff --check`와 `git status --short`로 작업 범위를 확인한다.
- [x] **Step 9: 인계.** 실제 final JSON, assets 폴더, preview, 검수 기록을 링크한다. verified extraction과 공식 정답 보유 여부를 구분한다. 사용자 승인된 경우 final 자료와 도구의 정확한 path만 `data(textbook): extract all exercises with redrawn figures`로 커밋하며, R 및 기존 unrelated untracked 파일은 stage하지 않는다.

## 자체 검토와 실행 인계

- 설계 범위: 원본 보존·14장·44쪽·원문 혼합 블록·직접 SVG·표 데이터·출처·필기 분리·미해결 보류·시각 검증·충돌 방지가 Tasks 1–6에 배정돼 있다.
- 인터페이스: 모든 자료 필드는 고정 데이터 인터페이스를 따른다. validate와 publish는 같은 payload 함수와 manifest 계약을 사용한다. preview 위치는 제작자료이며 assets/origin 링크 기준도 동일하다.
- 실패 사례: Review Focus의 다섯 항목을 소유 Task의 테스트에 배정했다. live 대조를 synthetic tests 통과로 대체하지 않는다.
- 구현 순서: Task 3은 Task 2, Task 4는 Tasks 1–3, Task 5는 Tasks 2–3, Task 6은 전체를 요구한다. 스키마가 바뀌면 전사 시작 전에 계약을 정리한다.
- 권장 실행은 Native이다. 공통 스키마·모델·전사가 밀접하게 연결되고 최종 44쪽과 모든 자산의 대조에 같은 맥락이 필요하다. 승인된 실행 방식에 따라 실행 스킬을 사용한다.
- 이 문서는 계획이다. 도구·연습문제 JSON·SVG 생성이나 커밋·푸시는 계획 작성 턴에서 실행하지 않는다.

실행 결과(2026-10-12): 213문항, 224보기, 70소문항, 39그림+7표. 38 tests passed, 최종 --complete PASS. 원본14 PDF만 9845996에 커밋했다. 실행 중 결정과 검수 범위는 교과서/제작자료/verification.md에 기록했다.
