from fractions import Fraction


def input_matrix():
    while True:
        try:
            n = int(input("행렬의 크기 n (양의 정수): "))
            if n <= 0:
                raise ValueError
            break
        except ValueError:
            print("입력 오류: n은 양의 정수여야 합니다.")

    matrix = []
    print(f"{n} × {n} 행렬을 행 단위로 입력하세요. (공백 구분)")
    print("정수, 소수, 분수 입력 가능: 예) 1 0.5 2/3")
    for i in range(n):
        while True:
            try:
                values = input(f"{i + 1}행: ").split()
                if len(values) != n:
                    print(f"입력 오류: 원소를 정확히 {n}개 입력하세요.")
                    continue
                row = [Fraction(value) for value in values]
                matrix.append(row)
                break
            except (ValueError, ZeroDivisionError):
                print("입력 오류: 유효한 숫자를 입력하세요. 분모는 0일 수 없습니다.")
    return matrix


def minor_matrix(matrix, row, col):
    return [
        [value for j, value in enumerate(values) if j != col]
        for i, values in enumerate(matrix) if i != row
    ]


def determinant(matrix):
    n = len(matrix)
    # 1 × 1 행렬의 여인수를 계산할 때 필요한 빈 행렬의 행렬식.
    if n == 0:
        return Fraction(1)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    return sum(
        ((-1) ** j * matrix[0][j] * determinant(minor_matrix(matrix, 0, j))
         for j in range(n) if matrix[0][j] != 0),
        Fraction(0),
    )


def inverse_by_determinant(matrix):
    det = determinant(matrix)
    if det == 0:
        raise ValueError("행렬식이 0이므로 역행렬이 존재하지 않습니다.")
    n = len(matrix)
    # 결과의 [i][j]에는 여인수 [j][i]를 넣어 전치한다.
    return [
        [Fraction((-1) ** (i + j) * determinant(minor_matrix(matrix, j, i)))
         / det for j in range(n)]
        for i in range(n)
    ]


def inverse_by_gauss_jordan(matrix, show_steps=False):
    n = len(matrix)
    augmented = [
        [Fraction(value) for value in matrix[i]]
        + [Fraction(int(i == j)) for j in range(n)]
        for i in range(n)
    ]
    if show_steps:
        print_matrix(augmented, "초기 확대행렬 [A | I]", split=n)

    for col in range(n):
        pivot_row = next(
            (row for row in range(col, n) if augmented[row][col] != 0), None
        )
        if pivot_row is None:
            raise ValueError("0이 아닌 피벗을 찾을 수 없어 역행렬이 존재하지 않습니다.")
        if pivot_row != col:
            augmented[col], augmented[pivot_row] = augmented[pivot_row], augmented[col]
            if show_steps:
                print_matrix(augmented, f"행 교환: R{col + 1} ↔ R{pivot_row + 1}", split=n)

        pivot = augmented[col][col]
        augmented[col] = [value / pivot for value in augmented[col]]
        if show_steps:
            print_matrix(augmented, f"피벗을 1로: R{col + 1} / ({pivot})", split=n)

        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            if factor == 0:
                continue
            augmented[row] = [
                augmented[row][j] - factor * augmented[col][j]
                for j in range(2 * n)
            ]
            if show_steps:
                print_matrix(
                    augmented,
                    f"열 소거: R{row + 1} - ({factor}) × R{col + 1}", split=n,
                )
    return [row[n:] for row in augmented]


def multiply(left, right):
    """원본 행렬과 역행렬의 곱을 검산한다."""
    n = len(left)
    return [
        [sum(left[i][k] * right[k][j] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]


def print_matrix(matrix, title, split=None):
    print(f"\n{title}")
    width = max(len(str(value)) for row in matrix for value in row)
    for row in matrix:
        cells = [str(value).rjust(width) for value in row]
        if split is not None:
            cells.insert(split, "|")
        print("[ " + "  ".join(cells) + " ]")


def main():
    print("=== 두 가지 방법으로 역행렬 구하기 ===")
    try:
        matrix = input_matrix()
    except (EOFError, KeyboardInterrupt):
        print("\n입력이 중단되어 프로그램을 종료합니다.")
        return

    print_matrix(matrix, "입력 행렬 A")
    print(f"\ndet(A) = {determinant(matrix)}")

    # 한 방법에서 예외 발생시 독립적 실행?으로 해결?
    results = []
    methods = [
        ("행렬식 방법", inverse_by_determinant),
        ("가우스-조던 방법", lambda a: inverse_by_gauss_jordan(a, show_steps=True)),
    ]
    for name, method in methods:
        print(f"\n--- {name} ---")
        try:
            result = method(matrix)
            print_matrix(result, f"{name}으로 계산한 역행렬")
            results.append(result)
        except ValueError as error:
            print(f"오류: {error}")
            results.append(None)

    if all(result is not None for result in results):
        print("\n비교 결과:", "두 역행렬이 정확히 일치합니다."
              if results[0] == results[1] else "두 역행렬이 일치하지 않습니다.")
        n = len(matrix)
        identity = [[int(i == j) for j in range(n)] for i in range(n)]
        for (name, _), result in zip(methods, results):
            product = multiply(matrix, result)
            print_matrix(product, f"{name} 검산: A × A⁻¹")
            print("검산 성공: 단위행렬입니다." if product == identity else "검산 실패")
    elif all(result is None for result in results):
        print("\n비교 결과: 두 방법 모두 역행렬이 존재하지 않는 것으로 판단했습니다.")
    else:
        print("\n비교 결과: 두 방법의 역행렬 존재 여부 판단이 다릅니다.")


if __name__ == "__main__":
    main()
