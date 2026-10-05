def input_matrix_size() -> tuple[int, int]:
    """Запросить у пользователя натуральные размеры матрицы."""
    while True:
        try:
            n = int(input("Введите число строк: "))
            m = int(input("Введите число столбцов: "))
        except ValueError:
            print("Ошибка: введите целые числа.")
            continue
        if n > 0 and m > 0:
            return n, m
        print("Ошибка: размеры должны быть натуральными числами.")


def matrix_init(n: int, m: int) -> list[list[float]]:
    """Считать матрицу размером n x m построчно."""
    matrix = []
    for i in range(n):
        while True:
            row = input(f"Введите строку {i + 1} из {m} чисел: ").split()
            if len(row) != m:
                print(f"Ошибка: нужно ровно {m} чисел.")
                continue
            try:
                matrix.append([float(x) for x in row])
                break
            except ValueError:
                print("Ошибка: все элементы должны быть числами.")
    return matrix


def matrix_print(matrix: list[list[float]]) -> None:
    """Вывести элементы матрицы по столбцам."""
    for column in zip(*matrix):
        print(*column)


def main() -> None:
    """Запустить консольную программу."""
    n, m = input_matrix_size()
    matrix = matrix_init(n, m)
    matrix_print(matrix)


if __name__ == "__main__":
    main()
