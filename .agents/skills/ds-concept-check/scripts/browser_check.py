#!/usr/bin/env python3
"""확인문제 HTML 을 Playwright 로 실제 조작해 보는 발행 게이트.

CLI: browser_check.py <확인문제 html> --src <자료_확인문제 폴더> --out <json> [--shots <dir>]

- serve_root(기본 저장소 루트)를 127.0.0.1 빈 포트 http.server 로 띄운다(끝나면 끈다).
- 1280×900·375×812 × light·dark 4회. 매 회 콘솔 error·.katex-error·가로 넘침을 본다.
- 객관식: 오답 클릭 → 상태 문구·보기별 설명 → 다시 풀기 → 정답 클릭.
- 값 입력(short): 허용답의 소문자·공백 변형을 넣고 '답 확인' → 맞음 상태('자동 일치').
- 새로고침하면 선택·입력이 비어야 한다(저장소 null). 복기 버튼이 있어야 한다.
- CDN 의 KaTeX·Pretendard 는 ds-problem-explain 의 같은 버전 로컬 사본으로 응답한다(네트워크 무관).
- 실패는 멈추지 않고 모아 JSON 에 남기며 하나라도 있으면 exit 1.
"""
from __future__ import annotations

import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
from urllib.parse import quote

import _paths
import build
import render

VIEWPORTS = [(1280, 900), (375, 812)]
THEMES = ["light", "dark"]
ACTION_TIMEOUT = 3000
NAV_TIMEOUT = 20000
SETTLE_MS = 600  # 화면 전환 애니메이션이 끝난 뒤 찍는다
SHORT_CORRECT = "자동 일치"  # review-interaction.js 가 short 정답일 때 .review-status 에 쓰는 글
VENDOR = _paths.REPO / ".agents" / "skills" / "ds-problem-explain" / "assets" / "vendor"
CDN_MAP = {"https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/": VENDOR / "katex",
           "https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/": VENDOR / "pretendard"}
CONTENT_TYPES = {".css": "text/css", ".js": "application/javascript", ".woff2": "font/woff2",
                 ".woff": "font/woff", ".ttf": "font/ttf"}


def route_external(origin: str, served: set[str], blocked: set[str]):
    """고정 버전 CDN 파일은 로컬 사본으로 응답하고, 그 밖의 외부 요청은 막고 기록한다."""
    def handle(route):
        url = route.request.url
        if url.startswith(origin) or url.startswith(("data:", "blob:")):
            return route.continue_()
        for prefix, folder in CDN_MAP.items():
            if url.startswith(prefix):
                local = folder / url[len(prefix):].split("?")[0].split("#")[0]
                if local.is_file():
                    served.add(url)
                    return route.fulfill(path=str(local),
                                         content_type=CONTENT_TYPES.get(local.suffix, "application/octet-stream"))
        blocked.add(url)
        return route.abort()
    return handle


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def short_variant(answer: dict) -> str:
    """정답과 대소문자·공백이 다른 허용답(소문자, 공백 있는 것 우선). 없으면 canonical.lower()."""
    canonical = answer["canonical"]
    pool = list(answer.get("accepted", [])) + render.accepted_variants(canonical)
    cands = [v.lower() for v in pool if v.lower() != canonical]
    spaced = [v for v in cands if " " in v]
    return (spaced or cands or [canonical.lower()])[0]


class Run:
    """뷰포트 × 테마 한 번. 예외 대신 실패를 모은다."""

    def __init__(self, page, label: str, origin: str):
        self.page, self.label, self.origin = page, label, origin
        self.failures: list[str] = []
        self.errors: list[str] = []
        self.served: set[str] = set()
        self.blocked: set[str] = set()
        page.on("pageerror", lambda e: self.errors.append(f"페이지 오류: {e}"))
        page.on("console", lambda m: self.errors.append(f"콘솔 error: {m.text}") if m.type == "error" else None)
        page.on("requestfailed", lambda r: self.errors.append(f"요청 실패: {r.url}") if r.url.startswith(origin) else None)
        page.on("response", lambda r: self.errors.append(f"HTTP {r.status}: {r.url}")
                if r.status >= 400 and r.url.startswith(origin) else None)
        page.context.route("**/*", route_external(origin, self.served, self.blocked))

    def expect(self, ok: bool, what: str) -> bool:
        if not ok:
            self.failures.append(f"{self.label}: {what}")
        return ok

    def step(self, what: str, fn):
        try:
            return fn()
        except Exception as e:  # Playwright TimeoutError 등: 기록하고 계속
            self.failures.append(f"{self.label}: {what}: {type(e).__name__}: {str(e).splitlines()[0]}")
            return None

    def go(self, card: str):
        self.page.evaluate("(id) => { location.hash = id; }", card)
        self.page.locator(f"#{card}").wait_for(state="visible")

    def page_checks(self, where: str):
        page = self.page
        self.expect(page.locator(".katex-error").count() == 0, f"{where}: 수식 렌더 오류(.katex-error)")
        self.expect(page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), f"{where}: 가로 넘침")


def check_mcq(run: Run, item: dict):
    page, cid = run.page, item["id"]
    run.go(cid)
    buttons = page.locator(f"#{cid} .review-choice")
    ids = [o["id"] for o in item["options"]]
    run.expect(buttons.count() == len(ids), f"{cid}: 보기 버튼 {buttons.count()}개 ≠ {len(ids)}")
    right = ids.index(item["answer"])
    wrong = (right + 1) % len(ids)
    buttons.nth(wrong).click()
    run.expect(buttons.nth(wrong).get_attribute("data-selected") == "true", f"{cid}: 오답 선택 표시 없음")
    status = (page.locator(f"#{cid} .review-status").text_content() or "").strip()
    run.expect(bool(status), f"{cid}: 오답 후 채점 상태 문구 없음")
    run.expect(page.locator(f"#{cid} .review-diagnostic:visible").count() >= 1, f"{cid}: 오답 후 진단 설명이 보이지 않음")
    page.locator(f"#{cid} .review-reset").click()
    run.expect(page.locator(f"#{cid} .review-choice[data-selected='true']").count() == 0, f"{cid}: 다시 풀기 뒤 선택 남음")
    buttons.nth(right).click()
    run.expect(buttons.nth(right).get_attribute("data-result") == "correct", f"{cid}: 정답 클릭 후 정답 표시 없음")
    return True


def check_short(run: Run, item: dict):
    page, cid = run.page, item["id"]
    run.go(cid)
    value = short_variant(item["answer"])
    page.locator(f"#{cid} .short-input input[type=text]").fill(value)
    page.locator(f"#{cid} .check-answer").click()
    status = (page.locator(f"#{cid} .review-status").text_content() or "").strip()
    run.expect(status == SHORT_CORRECT, f"{cid}: 허용답 '{value}' 입력 뒤 상태가 '{status}' (기대 '{SHORT_CORRECT}')")
    # 템플릿이 풀이(details)를 오른쪽 패널 .aid 로 옮긴다. 375 폭에서는 패널이 접혀 있어 open 만 본다.
    opened = page.locator(f".aid[data-card-id='{cid}'] details.solution[open]:not([hidden])").count()
    run.expect(opened == 1, f"{cid}: 답 확인 뒤 풀이가 열리지 않음")
    return True


def check_run(run: Run, url: str, items: list[dict], shots: Path | None, tag: str) -> dict:
    page = run.page
    page.goto(url, wait_until="load")
    run.page_checks("시작 화면")
    checked = 0
    for n, item in enumerate(items):
        fn = check_short if item["format"] == "short" else check_mcq
        if run.step(f"{item['id']}: 조작", lambda fn=fn, item=item: fn(run, item)):
            checked += 1
        if n == 0 and shots is not None:
            shot = shots / f"{tag}-{item['id']}.png"
            run.step("스크린샷 첫 문항", lambda: (page.wait_for_timeout(SETTLE_MS), page.screenshot(path=str(shot))))
        run.page_checks(item["id"])
    run.expect(page.locator('button:has-text("복기")').count() >= 1, "복기 프롬프트 버튼 없음")
    if shots is not None:
        shot = shots / f"{tag}-last.png"
        run.step("스크린샷 마지막 화면", lambda: (page.wait_for_timeout(SETTLE_MS), page.screenshot(path=str(shot))))
    if page.locator("#solved-btn").is_visible():  # 푼 문제 표시를 눌러 둬도 새로고침하면 사라져야 한다
        run.step("푼 문제로 표시", lambda: page.locator("#solved-btn").click())
    run.step("새로고침", lambda: page.reload(wait_until="load"))
    progress = (page.locator("#progress-n").text_content() or "").strip()
    run.expect(progress == "0", f"새로고침 뒤 푼 문제 수가 {progress} (기대 0)")
    run.expect(page.locator(".review-choice[data-selected='true']").count() == 0, "새로고침 뒤 선택 남음")
    values = run.step("새로고침 뒤 입력값 읽기", lambda: page.locator(".short-input input[type=text]").evaluate_all(
        "els => els.map(e => e.value)")) or []
    run.expect(all(v == "" for v in values), f"새로고침 뒤 입력값 남음: {values}")
    saved = run.step("새로고침 뒤 진행 기록 읽기", lambda: page.evaluate(
        "Object.keys(localStorage).filter(k => k.startsWith('od-review-solved:'))")) or []
    run.expect(saved == [], f"진행 기록이 localStorage 에 남음: {saved}")
    return {"items_checked": checked, "items": len(items)}


def check(html: Path, out: Path, shots: Path | None, *, src: Path, serve_root: Path | None = None,
          viewports=VIEWPORTS, themes=THEMES) -> dict:
    from playwright.sync_api import sync_playwright
    html = Path(html).resolve()
    root = Path(serve_root if serve_root is not None else _paths.REPO).resolve()
    if not html.is_relative_to(root):
        raise ValueError(f"HTML 이 서버 루트 밖에 있습니다: {html} (루트 {root})")
    items = build.load_source(src)["items"]
    report = {"html": html.relative_to(root).as_posix(), "sha256": sha256(html), "viewports": [f"{w}x{h}" for w, h in viewports],
              "themes": list(themes), "runs": [], "failures": []}
    if shots is not None:
        shots = Path(shots)
        shots.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        origin = f"http://127.0.0.1:{server.server_port}/"
        url = origin + quote(html.relative_to(root).as_posix())
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                for width, height in viewports:
                    for theme in themes:
                        ctx = browser.new_context(viewport={"width": width, "height": height})
                        page = ctx.new_page()
                        page.emulate_media(color_scheme=theme)
                        page.set_default_timeout(ACTION_TIMEOUT)
                        page.set_default_navigation_timeout(NAV_TIMEOUT)
                        run = Run(page, f"{width}x{height} {theme}", origin)
                        detail = run.step("검사", lambda: check_run(run, url, items, shots, f"{width}x{height}-{theme}")) or {}
                        run.failures += [f"{run.label}: {e}" for e in run.errors]
                        report["runs"].append({"label": run.label, "detail": detail, "failures": run.failures,
                                               "cdn_served_locally": len(run.served),
                                               "external_blocked": sorted(run.blocked)})
                        report["failures"] += run.failures
                        ctx.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
    report["status"] = "fail" if report["failures"] else "pass"
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="확인문제 브라우저 조작 검사")
    parser.add_argument("html", type=Path)
    parser.add_argument("--src", type=Path, required=True, help="자료_확인문제_<범위>_<슬러그> 폴더")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shots", type=Path)
    args = parser.parse_args(argv)
    try:
        report = check(args.html, args.out, args.shots, src=args.src)
    except (ValueError, build.BuildError) as e:
        print(f"browser: {e}", file=sys.stderr)
        return 1
    print(f"browser: {report['status']} · 실행 {len(report['runs'])}회 · 실패 {len(report['failures'])}건 → {args.out}")
    for line in report["failures"][:20]:
        print("  " + line)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
