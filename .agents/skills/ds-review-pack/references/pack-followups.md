# 기본 팩 발행 후 문제설명과 확인문제

## 준비

| 모드 | 문제설명 | 확인문제 |
|---|---|---|
| 신규 (`MMDD`·`MMDD-MMDD`) | 문항이 있으면 담당자 시작 | 별도 담당자 시작. 둘 다 가능하면 병렬 |
| `update-existing`·`revise-existing` | 문항이 있으면 담당자 시작 | 건너뜀. 기존 확인문제 보존 |
| `bank` | 건너뜀 | 건너뜀 |

생성 시작 전에 해당 모드에 필요한 형제 스킬의 `SKILL.md`와 실행기 존재를 확인한다. 문제설명은 `ds-problem-explain/scripts/mpe_cli.py`, 확인문제는 `ds-concept-check/scripts/`의 `concept_release.py`·`check.py`·`build.py`·`blind.py`·`browser_check.py`다. 누락이면 경로와 오류를 보고하며 시작을 중단한다. 경로는 `REPO/.agents/skills/` 기준이다.

## 병렬 시작

1. 기본 팩과 필요한 PDF가 발행된 후 시작한다. 메인은 `REPO`와 `RANGE`를 고정하고, 문제설명에는 이번에 발행한 `.pack/자료_복습팩/복습문제_<range>_<slug>.json`의 정확한 절대 경로(`ABS_REVIEW`)를 지정한다. 0문항이면 설명만 `skipped`다. 확인문제는 0문항 기본 팩에서도 근거가 있으면 진행한다.
2. 메인이 저장소 밖에 서로 겹치지 않는 고유하고 비어 있는 `EXPLAIN_RUN`, `CONCEPT_RUN`을 지정한다. 실행할 분기의 준비 명령만 실행한다. 문제설명은 메인이 원고·기존 설명의 해시를 RUN 옆에 기록하고, 확인문제는 작업용 `SRC`를 받는다. 준비에 실패한 분기는 보류하고 가능한 분기는 시작한다.

   ```bash
   python3 -B "$EXPLAIN_GATE" prepare --repo "$REPO" --review "$ABS_REVIEW" --run "$EXPLAIN_RUN"
   python3 -B "$CONCEPT_CLI" prepare --repo "$REPO" --range "$RANGE" --run "$CONCEPT_RUN"
   ```

   `CONCEPT_CLI`는 위 `concept_release.py`, `EXPLAIN_GATE`는 이 스킬의 `scripts/followup_explain.py` 절대 경로다.

3. 두 분기가 있으면 새 컨텍스트의 담당자 둘을 모두 띄운 뒤 기다린다. 문제설명 담당자에게는 `REPO`, `ABS_REVIEW`, `EXPLAIN_RUN`, [문제설명 절차](problem-explain.md) 경로를 보낸다. 확인문제 담당자에게는 `REPO`, `RANGE`, `CONCEPT_RUN`, 준비한 `SRC`, 형제 `ds-concept-check/SKILL.md` 경로를 보낸다. 각 지시에는 **작업본까지만** 작성한다고 명시한다. 두 후속 작업의 검사와 확인문제 모델 선정은 각 스킬을 그대로 따른다.
4. 담당자와 그 하위 작성자·풀이자는 배정된 RUN 범위에만 쓴다. 임시 파일도 해당 RUN 아래에 두고 Python 실행에는 `-B` 또는 `PYTHONDONTWRITEBYTECODE=1`을 쓴다. 공개 팩과 출처는 읽기 전용이다. 담당자가 반환하는 것은 `ready|withheld|skipped`, 이유 또는 미해결 항목, RUN·검토 기록 경로와 9단계 보고용 수치다. 수동 화면을 직접 열어 검사한 기록이 필요하며 메인은 문서 본문이나 캡처를 받아 다시 읽지 않는다. 새 컨텍스트나 실제 화면 도구가 확보되지 않으면 해당 작업을 보류한다.

## 블라인드 중계

확인문제 담당자가 독립 작성자와 회차마다 새 풀이자를 호출한다. 중첩 호출을 지원하지 않거나 슬롯을 확보할 수 없으면 메인에게 호출을 맡긴다. 담당자는 회차, 풀이 브리프 경로와 채운 내용, 현재 사본, 작업용 정리노트 MD, 지정된 답안 경로만 넘긴다. 메인은 상속 이력이 없는 새 컨텍스트에서 같은 모델 규칙을 적용하고 그 셋만 읽힌다. 풀이 브리프의 단독 모드 답안 요약은 이 호출에서 생략하며, 풀이자와 메인은 답안 경로만 담당자에게 전달한다. 풀이자에게 정답·`items.json`·`objectives.json`·장부·이전 답안이나 그 내용을 전달하지 않는다. 반려 문항만 최대 r3까지 검증한다. 작성자 호출·재호출을 중계할 때도 해당 스킬의 별도 브리프·모델 규칙·수정 상한을 적용한다.

## 발행

메인만 발행한다. 두 결과는 각각 판정한다. 메인은 자신이 지정한 RUN과 현재 팩을 사용해서 `ready`마다 해당 명령을 호출한다. `withheld`이면 기존 공개 파일과 RUN의 작업본을 보존하고 이유를 보고한다. 한쪽의 오류가 다른 쪽의 발행을 막지 않는다. `skipped`면 발행 없이 사유를 보고한다.

- 문제설명 발행기는 기본 팩 잠금 안에서 `run.json`·`source.json`의 저장소·대상 하나, 지정한 유효 JSON 원고, 준비 당시 원고·기존 설명의 해시를 대조한다. 이어 기존 `mpe_cli.py publish`가 현재 산출물·참조 해시와 네 검토를 재검증하고 백업한 뒤 발행한다.
- 확인문제 발행기는 지정한 저장소·범위·RUN의 준비 기록, 규칙 검사와 r3 이내 장부, 현재 작업본의 기계 검사·실제 화면 검토, 배치, 근거와 기존 파일 해시를 다시 확인한다. 확인문제 HTML과 네 JSON만 갱신한다.

```bash
python3 -B "$EXPLAIN_GATE" publish --repo "$REPO" --review "$ABS_REVIEW" --run "$EXPLAIN_RUN"
python3 -B "$CONCEPT_CLI" publish --repo "$REPO" --range "$RANGE" --run "$CONCEPT_RUN"
```

발행 명령이 실패하면 해당 작업만 `withheld`로 기록한다. 복습노트의 기본 팩·PDF와 각 후속 작업의 기존 파일은 해당 작업의 실패로 되돌리지 않는다. 작업별 상태·이유·검토·공개 경로·백업을 9단계에 보고한다.
