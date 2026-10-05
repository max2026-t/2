from unittest.mock import patch

from src.main import input_matrix_size, matrix_init, matrix_print


def test_matrix_print_outputs_columns(capsys):
    matrix_print([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert capsys.readouterr().out == "1.0 4.0\n2.0 5.0\n3.0 6.0\n"


def test_input_matrix_size_accepts_positive_integers():
    with patch("builtins.input", side_effect=["2", "3"]):
        assert input_matrix_size() == (2, 3)


def test_input_matrix_size_retries_invalid_values(capsys):
    with patch("builtins.input", side_effect=["x", "2", "0", "2", "3"]):
        assert input_matrix_size() == (2, 3)
    output = capsys.readouterr().out
    assert "введите целые числа" in output
    assert "размеры должны быть натуральными" in output


def test_matrix_init_accepts_float_values():
    with patch("builtins.input", side_effect=["1.5 2 -3"]):
        assert matrix_init(1, 3) == [[1.5, 2.0, -3.0]]


def test_matrix_init_retries_wrong_length(capsys):
    with patch("builtins.input", side_effect=["1 2", "1 2 3"]):
        assert matrix_init(1, 3) == [[1.0, 2.0, 3.0]]
    assert "нужно ровно 3 чисел" in capsys.readouterr().out


def test_matrix_init_retries_non_numeric_values(capsys):
    with patch("builtins.input", side_effect=["1 x", "1 2"]):
        assert matrix_init(1, 2) == [[1.0, 2.0]]
    assert "элементы должны быть числами" in capsys.readouterr().out
