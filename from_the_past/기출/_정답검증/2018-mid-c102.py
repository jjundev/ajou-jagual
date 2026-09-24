"""2018-mid-c102 정답 검증. 실행하면 '<문항 id>\t<답>'을 출력한다.
5~16번은 2018-mid-c024의 5~16번과 같은 문항이라 같은 폴더의 c024 검증 파일 함수를 그대로 쓴다."""
import importlib.util, os

SRC = "2018-mid-c102"
HERE = os.path.dirname(os.path.abspath(__file__))


def load_c024():
    for name in ("2018-mid-c024.py", "verify_2018-mid-c024.py"):  # 저장소 이름, 실행 폴더 이름
        p = os.path.join(HERE, name)
        if os.path.exists(p):
            spec = importlib.util.spec_from_file_location("c024", p)
            m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
            return m
    raise FileNotFoundError("2018-mid-c024 검증 파일이 같은 폴더에 없음")


# 1~4: 정의형 빈칸 — 실행으로 확인할 수 없음(원본 답)
def q1(): return "순환"
def q2(): return "스택"
def q3(): return "트리"
def q4(): return "높이"


if __name__ == "__main__":
    c024 = load_c024()
    for i in range(1, 17):
        f = globals().get(f"q{i}") or getattr(c024, f"q{i}")
        print(f"{SRC}-q{i}\t{f()}")
