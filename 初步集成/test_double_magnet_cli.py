"""Tests for the double-magnet command-line adapter."""

import pytest

from double_magnet_cli import parse_cli_args, run_from_options
from modular_double_magnet_benchmark import make_mesher


def test_parse_cli_args_maps_names_to_typed_options():
    options = parse_cli_args(
        [
            "--d",
            "0",
            "2.5",
            "--p",
            "3",
            "--h-near",
            "1.2",
            "--h-far",
            "5",
            "--compare",
            "--error-plot",
            "error.png",
        ]
    )
    assert options.displacements_mm == (0.0, 2.5)
    assert options.degree == 3
    assert options.h_near_mm == 1.2
    assert options.h_far_mm == 5.0
    assert options.compare
    assert options.error_plot_path == "error.png"
    assert options.comparison_requested


@pytest.mark.parametrize(
    "arguments",
    [
        ["--p", "0"],
        ["--h-near", "0"],
        ["--h-far", "-1"],
        ["--h-near", "nan"],
        ["--h-far", "inf"],
        ["--d", "-1"],
        ["--d", "nan"],
        ["--h-near", "7", "--h-far", "6"],
    ],
)
def test_parse_cli_args_rejects_invalid_solve_parameters(arguments):
    with pytest.raises(SystemExit):
        parse_cli_args(arguments)


@pytest.mark.parametrize(
    "arguments",
    [
        (-1.0, 1.5, 6.0),
        (0.0, 0.0, 6.0),
        (0.0, 7.0, 6.0),
    ],
)
def test_python_api_rejects_invalid_geometry_controls(arguments):
    with pytest.raises(ValueError):
        make_mesher(*arguments)


def test_run_from_options_injects_all_solve_parameters(capsys):
    options = parse_cli_args(
        ["--d", "1", "3", "--p", "2", "--h-near", "1", "--h-far", "4"]
    )
    received = {}

    def fake_solve_many(displacements, **kwargs):
        received["displacements"] = displacements
        received.update(kwargs)
        return [
            {"d": d, "F0": [1.0, 2.0, 3.0], "F1": [-1.0, -2.0, -3.0]}
            for d in displacements
        ]

    results = run_from_options(options, fake_solve_many)
    assert len(results) == 2
    assert received == {
        "displacements": (1.0, 3.0),
        "p": 2,
        "h_near_mm": 1.0,
        "h_far_mm": 4.0,
        "show": False,
    }
    assert "F0=lower magnet" in capsys.readouterr().out
