# 교과서 연습문제 추출본

인쇄 원문만 전사한 UTF-8 JSON이다. 직접 작성한 정답·풀이를 포함하지 않는다. 필기는 observations, 원본 오류·외부 본문 참조는 issues에 분리한다. 인쇄 실행 예시는 content에 남긴다.

- ../[NN]_*_연습문제.json: 장마다 sources, chapters(1개), questions, assets를 저장한다.
- ../readme.md: 장별 파일 목록과 사용 안내.
- scripts/bank.py: 장별 파일을 메모리에서 합치고 파일명·장·출처·그림·중복 ID를 검사한다.
- question-bank.schema.json: 혼합 문항과 재귀 content 블록 계약.
- asset-models.json: 노드·연결·배열·표 셀 또는 직접 그린 vector primitives.
- inventory.json: 원본 44쪽의 독립 문항 인벤토리와 검토 기록.
- preview.html: 전체 문제와 새 그림 미리보기.
- verification.md, verification.json: 검수 범위와 현재 바이트 검토 기록.

문항 id는 ch05-q06 형식이다. content는 text/code/figure/table/subquestions를 순서대로 저장한다. asset 경로는 교과서 폴더 기준 상대 경로다. SVG는 흰 배경 위에서 표시한다. 표·배열의 인쇄 빈칸은 빈 문자열이며, 역슬래시 n은 JSON을 읽으면 원문 C 문자열의 역슬래시 n으로 복원된다.

## 제작자료 폴더에서 재검증

```sh
python3 -m venv /tmp/textbook-check-venv
/tmp/textbook-check-venv/bin/python -m pip install -r scripts/requirements.txt
/tmp/textbook-check-venv/bin/python scripts/validate.py .. --complete
/tmp/textbook-check-venv/bin/python -m pytest tests -q
```

source/model/SVG/JSON/inventory가 바뀌면 영향받은 원본·그림을 실제 재검토해야 한다. 해시 변경만으로 검토를 대신할 수 없다. publisher는 기존 파일 덮어쓰기를 거부한다.

검증·미리보기·자산 생성 CLI의 bank 인자는 JSON 파일이 아닌 교과서 폴더다. 배포 도구도 장별 JSON을 모두 검증한 뒤 별도 파일로 복사한다.

미리보기 재생성: `python scripts/preview.py ..`. 검토된 SVG는 자산 생성 도구가 덮어쓰지 않는다.
