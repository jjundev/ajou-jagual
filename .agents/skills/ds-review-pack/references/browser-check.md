# 브라우저 검증 (메인 에이전트)

## 서버
file:// 미리보기에서는 스크립트가 돌지 않는다. 빈 포트로 서버를 띄운다. 셸 상태는 Bash 호출 사이에 이어지지 않으므로 포트 번호를 먼저 출력해 두고, 이후 명령과 URL에는 그 숫자를 직접 쓴다.
1. 빈 포트 찾기(출력된 숫자가 `<port>`):
   ```bash
   python3 -c "import socket; s=socket.socket(); s.bind(('',0)); print(s.getsockname()[1])"
   ```
2. 서버 띄우기: Bash 도구의 `run_in_background: true`로 실행한다(명령 끝에 `&`를 붙이지 않는다).
   ```bash
   python3 -m http.server <port> --directory "<RUN>/repo"
   ```
3. URL: `http://localhost:<port>/복습노트/<range>/<파일명>` (한글 그대로).
4. 끝나면 서버를 종료한다: 그 백그라운드 작업을 멈추거나(TaskStop 등), `pkill -f "http.server <port>"`.

## 측정 전 준비
브라우저 창이 숨겨져 있으면 `document.documentElement.clientWidth`가 0이 되어 `hScroll`이 거짓 양성으로 나온다. 측정 전에 `resize_window`로 크기를 명시하고(`width: 1280`, `height: 900`) `document.documentElement.clientWidth > 0`을 확인한다. `.katex-mathml` 안 요소는 화면에 보이지 않으므로 넘침 원인으로 치지 않는다. 스크롤 직후 스크린샷은 늦게 반영될 수 있으니 1초쯤 기다린 뒤 찍는다.

## 가로 넘침 측정 (두 페이지 공통)
템플릿은 `body`를 고정하고 본문을 `.content` 안에서 스크롤하며, 한 번에 한 화면(토픽·카드)만 보여 준다. 그래서 `document.documentElement.scrollWidth`로는 넘침이 잡히지 않는다. 아래 `overflowScreens`로 화면을 하나씩 넘기며 `.content`를 잰다. 결과는 넘친 화면 id 목록이고, 비어 있어야 통과다. 목록이 나오면 그 화면에서 `.content`의 오른쪽 끝을 넘는 요소를 찾아 원인을 확인한다(`.katex-display`·`.table-wrap`·`pre` 안의 자체 가로 스크롤은 넘침이 아니다).
```js
async function overflowScreens() {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const scroller = document.querySelector('.content') || document.documentElement;
  const screens = Array.from(document.querySelectorAll('main .screen'));
  const over = [];
  for (const s of screens.length ? screens : [document.querySelector('main')]) {
    if (screens.length) { location.hash = s.id ? '#' + s.id : ''; await wait(150); }
    // 넘어올 때의 translateX(24px) 애니메이션이 넘침으로 잡히지 않게 끝낸다(숨은 창에서는 애니메이션이 멈춰 있다)
    document.getAnimations().forEach((a) => a.finish());
    if (scroller.scrollWidth > scroller.clientWidth + 1 || document.documentElement.scrollWidth > window.innerWidth + 1) over.push(s.id || 'hero');
  }
  location.hash = '';
  await wait(150);
  return over;
}
```

## 정리노트 (`mcp__Claude_Browser__javascript_tool`)
위 `overflowScreens` 정의를 같은 실행에 붙여 넣는다.
```js
await new Promise((r) => setTimeout(r, 1500));
const textNodes = Array.from(document.querySelectorAll('main *, #panel-right *')).filter((e) => !['SCRIPT', 'STYLE'].includes(e.tagName) && !e.closest('[hidden]'));
({
  katex: document.querySelectorAll('.katex').length,
  katexErrors: document.querySelectorAll('.katex-error').length,
  rawDollar: textNodes.some((e) => Array.from(e.childNodes).some((n) => n.nodeType === 3 && n.textContent.includes('$'))),
  sumsInPanel: document.querySelectorAll('#panel-right .sum').length,
  sumsLeftInMain: document.querySelectorAll('main .sum').length,
  hScroll: await overflowScreens(),
  widgets: Array.from(document.querySelectorAll('.widget')).map((w) => ({ id: w.id, drawn: Array.from(w.querySelectorAll('svg')).some((s) => !s.closest('[hidden]') && s.childElementCount > 0) })),
})
```
통과: `katexErrors: 0`, `rawDollar: false`, `sumsInPanel`이 manifest에서 `layers`가 빈 목록이 아닌 토픽 수, `sumsLeftInMain: 0`, `hScroll: []`, 모든 위젯 `drawn: true`. `read_console_messages`에 오류 없음.

개념 토픽 하나로 넘겨(`location.hash = '#<토픽 id>'`) 오른쪽 "페이지 요약" 패널에 그 토픽의 요약이 보이는지 스크린샷으로 확인한다(1280px 이상에서는 패널이 기본으로 열린다).

위젯마다 그 토픽으로 넘긴 뒤 슬라이더 하나를 바꾸고(`input` 이벤트) readout 값이 `.widget-static` 표의 같은 설정 값과 같은지 확인한다.

## 모바일·다크
`resize_window`(`preset: "mobile"`, `colorScheme: "dark"`) → 새로고침 → `clientWidth > 0` 확인 → 위 스크립트 재실행(`hScroll: []`) → 스크린샷으로 그림·위젯 글자가 보이는지 확인 → 상단 바의 테마 버튼(`#theme-toggle`)을 눌러 `document.body` 배경색이 바뀌고 `aria-label`이 반대 모드로 바뀌는지 확인한 뒤 `localStorage.removeItem('od-theme')`로 지운다 → `preset: "desktop"`, `colorScheme: "light"`로 되돌린다.

## 복습문제
측정 전에 다시 `resize_window`(`width: 1280`, `height: 900`) → `clientWidth > 0` 확인(앞 단계의 `preset: "desktop"`은 창 크기를 창 자체 크기로 되돌려 숨은 창에서는 0이 될 수 있다). 이번에도 `overflowScreens` 정의를 붙여 넣는다.
```js
await new Promise((r) => setTimeout(r, 1500));
document.querySelectorAll('details').forEach((d) => { d.open = true; });
await new Promise((r) => setTimeout(r, 300));
({
  cards: document.querySelectorAll('article.card').length,
  aidGroups: document.querySelectorAll('#panel-right .aid').length,
  katexErrors: document.querySelectorAll('.katex-error').length,
  hScroll: await overflowScreens(),
})
```
통과: `cards`와 `aidGroups`가 모두 manifest 문제 수, `katexErrors: 0`, `hScroll: []`. 첫 카드로 넘겨 오른쪽 "풀이 도움" 패널에 그 카드의 원문·힌트·풀이가 보이는지, 상단 "정리노트" 링크가 노트로 이동하는지 확인한다.

## 마무리
모든 검사가 끝나면 `resize_window`(`preset: "desktop"`, `colorScheme: "light"`)로 되돌리고 서버를 종료한다(위 "서버" 4).

## 패널 제목과 요약 계약
중앙 제목과 고정 패널 제목을 유지하고 오른쪽의 중복 주제·문항 제목은 출력하지 않는다. `sum-for`는 `.sums` 컨테이너의 유일한 ID로 보존하며 `aid-for`와 제거한 제목의 JavaScript 참조는 두지 않는다.

요약 항목 수에 고정 상한을 두지 않는다. 같은 토픽 본문의 핵심 개념·원리·성립 조건·혼동 구분을 압축하고, 본문에 없는 사실을 추가하지 않는다. 보충의 범위·출처·불확실성을 유지한다. 모든 학습 토픽의 일반·강조·주의·보충 핵심을 본문 주장, 대응 요약, 판정 또는 생략 이유로 대조한다. 누락은 unresolved로 기록하고 보완된 실제 요약을 다시 읽은 뒤 pass로 바꾼다. 기존 동반 MD와 실제 생성 원고를 동기화하고 동반 MD가 없으면 새 형식을 만들지 않는다.

브라우저는 HTTP 임시 stage에서 1280×900, 375×812 각각 light/dark로 검사한다. 요약·풀이 패널을 열어 중앙 제목 표시, 우측 중복 제목 없음, 토픽별 요약 하나와 정확한 내용, 표지 안내, 이전 요약 숨김, 수식 오류와 페이지 오류 0을 확인한다. 문제·원문 탭, 이전/다음, 힌트·풀이, 푼 문제 토글과 기존 read/solved 저장 키를 유지한다. missing-sum 실패 탐지와 no-panel legacy 검사를 유지한다.
