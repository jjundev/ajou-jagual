# 문맥 링크

기존 노트 HTML에서 실제 관련 article/section ID를 확인한다. 본문·위젯·스타일·스크립트·MD·PDF를 재생성하지 않는다. 연결 문장은 관찰할 대상을 말한다. 예: “매개변수에 복사된 값과 호출자의 변화를 [자료]에서 한 단계씩 확인해 보세요.”

자료 디렉터리의 note-links.json:

```json
{"notes":[{"note":"../../정리노트_0928_ArrayStructureList.html","links":[{"sectionId":"s1-swap","html":"../../$HTML","label":"값과 주소의 전달","before":"복사와 원본 변화를 ","after":"에서 확인해 보세요."}]}]}
```

`$HTML`은 save가 실제 파일명으로 치환한다. 이미 저장된 자료는 실제 파일명을 넣는다. 모든 경로는 매니페스트 기준 상대 경로이며 폴더를 옮겨도 관계를 유지한다.

```
node "S/scripts/link-notes.cjs" "MANIFEST" --dry-run
node "S/scripts/link-notes.cjs" "MANIFEST"
node "S/scripts/relink.cjs" "REPO" 0928 --dry-run
node "S/scripts/relink.cjs" "REPO" 0928
```

offset 파서는 주석·script/style/textarea/title 속 가짜 태그를 무시한다. ID가 정확히 하나인 article/section만 연결한다. formal 설명 뒤, 없으면 eli5 뒤 또는 제목 뒤에 넣는다. 그조차 없으면 해당 절 끝에 넣는다. 명세에 anchorId를 주면 그 위치를 확인한다. 누락·중복 절은 skipped이며 자료 자체는 남긴다.

URL 인코딩한 상대 href, target=_self, data-ds-interactive 표시. 같은 목적지가 이미 해당 절에 있으면 문구·rel을 보존하고 target만 필요한 경우 고친다. 같은 자료를 다른 절에 연결하는 것은 허용한다. 수정 전 backupDir 또는 노트 .pack/ds-interactive-backups에 원본 bytes를 백업한다.

매니페스트 없는 오래된 자료는 내용을 읽어 관련 절을 판단하고 명세를 새로 만든다. 파일명만 보고 임의 절에 붙이지 않는다. 노트 재생성 후 relink를 두 번 실행해 두 번째 unchanged를 확인한다. 최종 링크 클릭·현재 탭 이동·뒤로가기도 검증한다.
