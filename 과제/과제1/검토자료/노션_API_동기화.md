# 과제1 보고서 Notion API 동기화

## 현재 상태

- Notion 페이지: https://app.notion.com/p/HW1-Banker-s-Algorithm-Report-4b5b06d263bc8255b539819393d50d19
- `notion_sync.py push`를 사용해 기존 페이지 URL 안의 블록을 API로 갱신했다.
- 소스 분석의 여섯 함수 구획은 각각 2열 Notion `table` 블록이다. 첫 열은 복사 가능한 C 코드, 둘째 열은 기능 명세와 분석이다. 원래 코드의 줄바꿈은 셀 텍스트에 보존했다.
- UI로 가져온 이전 블록 112개는 Notion 휴지통에 보존했다. 갱신 전 API 응답과 Markdown은 `notion_api/before-*.json`, `notion_api/before-*.md`에 있다. `notion_api/manifest.json`에는 교체된 블록 ID가 있다.
- API로 만든 2열 컬럼 6개도 표 전환 뒤 휴지통에 보존했다. 전환 전후 기록은 `notion_api/before-table-*.json`, `notion_api/before-table-*.md`, `notion_api/table-layout.json`에 있다.
- API에서 다시 읽은 Markdown은 `../보고서_노션.md`에 있다. 이 파일은 표 셀의 여러 줄 텍스트를 `<br>`로 나타내는 Notion 확장 Markdown이다.
- 2026-09-26 입력 안내 끝의 `: ` 수정 후, 기존 함수 표의 코드 셀 3개와 공식 예제 출력 블록 3개만 Notion API로 갱신했다. 갱신 전 페이지 트리와 Markdown은 `notion_api/prompt-before-*.json/.md`에 보관했고, 재조회한 코드 셀 여섯 구획이 현재 `HW1.c` 및 `보고서.md`의 코드와 일치함을 확인했다.

## Notion에서 고친 뒤 확인하는 방법

프로젝트 루트에서 실행한다.

```bash
python3 과제/과제1/검토자료/notion_sync.py pull
```

이 명령은 Notion의 `GET /v1/pages/{page_id}/markdown`을 호출한다. 응답이 잘렸거나 알 수 없는 블록이 있으면 저장하지 않는다. 변경된 내용이 있으면 이전 다운로드 파일을 날짜가 붙은 백업으로 남긴 뒤 `과제/과제1/보고서_노션.md`를 갱신한다. 로컬 `보고서.md`는 자동으로 덮어쓰지 않는다.

이후 두 Markdown을 비교하고 Notion에서 직접 수정한 문장을 기준으로 보고서 원고를 검토한다. 함수별 2열 표는 Notion 블록이 기준이며, 최종 PDF는 Notion에서 내보낸 뒤 표 너비와 코드 텍스트 선택·복사가 가능한지 따로 확인한다.

## 재업로드 주의

현재 페이지의 API 업로드는 완료됐다. `push`를 다시 실행하면 기존 업로드 기록을 감지하고 중단한다. Notion에서 수정한 내용을 로컬 초안으로 덮어쓰지 않기 위해서다. 토큰은 환경변수 `NOTION_TOKEN`에서만 읽고 파일에 저장하지 않는다.

## 검증

```bash
python3 -m unittest discover -s 과제/과제1/검토자료 -p 'test_notion_sync.py' -v
```

표 전환 직후 Notion 블록 API에서 왼쪽 셀의 C 코드 6개를 다시 읽어 `HW1.c`와 일치함을 확인했다. Notion Markdown API도 표를 포함한 문서를 잘림 없이 반환했다.
