"""실제 콘솔 실행 기록 저장 및 핵심 동작 검증: python test_program.py"""

from fractions import Fraction as F
from pathlib import Path
import os
import subprocess
import sys

from main import inverse_by_determinant, inverse_by_gauss_jordan


ROOT = Path(__file__).resolve().parent
CASES = [
    ("00_student_digits", "2\n23 19\n22 30\n", "두 역행렬이 정확히 일치합니다."),
    ("01_normal_2x2", "2\n4 7\n2 6\n", "두 역행렬이 정확히 일치합니다."),
    ("02_swap_3x3", "3\n0 2 1\n1 1 0\n2 0 1\n", "행 교환: R1 ↔ R2"),
    ("03_singular", "2\n1 2\n2 4\n", "두 방법 모두 역행렬이 존재하지 않는"),
    ("04_single", "1\n5\n", "1/5"),
    ("05_input_recovery", "0\nx\n2\n1\na b\n1/0 2\n0.5 0\n0 2/3\n", "두 역행렬이 정확히 일치합니다."),
]


def run_tests():
    output_dir = ROOT / "execution_logs"
    output_dir.mkdir(exist_ok=True)
    for name, data, expected in CASES:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "main.py")], input=data,
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}, check=True,
        )
        assert not completed.stderr, completed.stderr
        assert expected in completed.stdout, name
        if name != "03_singular":
            assert completed.stdout.count("검산 성공") == 2, name
        (output_dir / f"{name}.txt").write_text(
            "[제공한 표준 입력]\n" + data + "\n[실제 표준 출력]\n" + completed.stdout,
            encoding="utf-8",
        )
        print(f"PASS: {name}")

    # 두 구현이 동일한 오답을 내는 경우도 잡도록 알려진 정답과 비교한다.
    matrix = [[F(4), F(7)], [F(2), F(6)]]
    expected = [[F(3, 5), F(-7, 10)], [F(-1, 5), F(2, 5)]]
    original = [row[:] for row in matrix]
    for method in (inverse_by_determinant, inverse_by_gauss_jordan):
        assert method(matrix) == expected
        assert matrix == original, "원본 행렬이 변경됨"
        for singular in ([[F(0)]], [[F(1), F(2)], [F(2), F(4)]]):
            try:
                method(singular)
            except ValueError:
                pass
            else:
                raise AssertionError("특이행렬 예외 누락")
    print("PASS: 알려진 정답, 원본 보존, 두 방법의 특이행렬 예외")


if __name__ == "__main__":
    run_tests()
