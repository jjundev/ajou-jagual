# Content review — 0928

강의 PDF p20,22,25의 실제 렌더링과 정리노트 HTML/.pack MD/STT를 대조했다. p22 swap의 함수 본문은 원문과 같다. 입력 템플릿과 헤더/int main(void), 비교 값 전달·동일주소, 나머지 두 함수는 학습용 보충이다. source.json/brief와 화면의 출처 안내가 이를 구분한다.

- value-address: call은 새 저장 공간, bind는 정수 또는 주소 값 복사. 각 매개변수 주소는 고유하다. tmp 선언은 미초기화, read→tmp 보관→둘째 read→첫 write→tmp read→둘째 write 순서가 원문과 같다. 값 모드는 caller 불변, 주소 모드는 caller 교환, 별칭 모드는 동일 대상 두 번이므로 첫 값 유지. 반환은 callee 자동 변수 수명만 종료한다.
- pointer-target: q 값을 p에 복사한다. *p write는 a만 바꾸고 p=NULL은 p만 바꾼다. caller q는 &a를 유지한다. NULL 모드는 bind까지 가능하고 첫 역참조에서 중단한다. 초기 안내는 NULL에도 맞게 특정 대상 가정을 제거했다.
- double-pointer: 단일 p는 q에 들어 있던 &a를 받고 재대입은 p만 바꾼다. 이중 pp는 &q를 받아 q 자체에 &b를 쓴다. next 주소는 b 정수를 읽지 않는다. NULL 모드의 bind와 역참조 설명은 실제 NULL 값·중단과 일치하도록 구분했다. a/b의 정수는 어느 모드에서도 변하지 않는다.

읽기와 쓰기 강조는 Snapshot의 reads/writes에 대응한다. 자기 주소·저장 주소·대상 값을 분리한다. 반환 후 저장 공간은 수명 종료의 과거 흔적이다. 주소는 기호이고 메모리 배치/ABI를 주장하지 않는다. C는 항상 값 전달이라는 안내를 제공하며 노트의 수업 표현을 고쳐 쓰지 않는다.

독립 Python 표는 모든 bind/declaration/write 값을 다른 언어의 정해진 계산으로 비교했다. 38개 조건, 144개 쓰기. PATH의 gcc/clang/cl 부재로 컴파일 실행을 주장하지 않는다. NULL은 정의되지 않은 동작 실행을 시도하지 않고 원인 단계 진단으로 확인한다.

판정: pass. NULL 문구 수정과 최종 리뷰 회귀 수정을 반영해 재빌드했고, browser-final의 18조합/852 Snapshot을 통과한 현재 preview를 확인했다. 저장 시 이 증거와 현재 해시를 함께 고정한다.


## 2026-10-17 UI 갱신
원본 scenario/source/trace와 실행 엔진은 사전 해시와 동일하다. 기존 내용 검토는 그대로 유효하며 Python 독립 검산38조건144건을 재실행했다. 변경은 Native 공통 셸, 패널/서랍/보기 및 실제 Pretendard400/500/600/700 포함 방식이다. 새 browser.json의 preview 해시를 재빌드 결과와 비교했다.
