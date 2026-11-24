from pathlib import Path
from runpy import run_path
from unittest.mock import patch

import pytest

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


@pytest.mark.parametrize("rows,columns", [(0, 0), (0, 2), (2, 0), (2, 2)])
def test_dimension_condition_combinations(rows, columns, capsys):
    with patch("builtins.input", side_effect=[str(rows), str(columns), "1", "3"]):
        result = input_matrix_size()
    valid = rows > 0 and columns > 0
    assert result == ((rows, columns) if valid else (1, 3))
    assert ("натуральными" in capsys.readouterr().out) is not valid


def test_matrix_console_entry_point(capsys):
    path = Path(__file__).resolve().parents[1] / "src" / "main.py"
    with patch("builtins.input", side_effect=["2", "2", "1 2", "3 4"]):
        run_path(str(path), run_name="__main__")
    assert capsys.readouterr().out == "1.0 3.0\n2.0 4.0\n"
