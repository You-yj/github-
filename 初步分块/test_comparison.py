"""Tests for the FEALPy-independent force comparison module."""

import csv

import numpy as np

from comparison import compare_force_results
from double_magnet_reference import (
    akoun_yonnet_force,
    ansys_reference_force,
)


def test_akoun_yonnet_d_zero_symmetry():
    force = akoun_yonnet_force(0.0)
    np.testing.assert_allclose(force[0], force[1], rtol=0.0, atol=1.0e-10)
    np.testing.assert_allclose(force, [0.588356, 0.588356], atol=1.0e-6)


def test_comparison_metrics_and_missing_reference():
    results = [
        {"d": 0.0, "F1": np.array([1.0, 2.0, 0.0])},
        {"d": 1.0, "F1": np.array([2.0, 4.0, 0.0])},
    ]
    comparison = compare_force_results(
        results,
        references={"reference": {0.0: [0.0, 2.0]}},
    )
    fx = comparison.metrics()["reference"]["Fx"]
    fy = comparison.metrics()["reference"]["Fy"]
    assert fx.count == 1
    assert fx.mae == 1.0
    assert fx.max_error_d == 0.0
    assert fy.count == 1
    assert fy.rmse == 0.0
    assert np.isnan(comparison.references["reference"][1]).all()


def test_csv_export(tmp_path):
    results = [{"d": 0.0, "F1": np.array([1.0, 2.0, 3.0])}]
    comparison = compare_force_results(
        results,
        references={"ref": lambda d: [0.5, 2.5]},
    )
    output = comparison.write_csv(tmp_path / "comparison.csv")
    with output.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream))
    assert rows[0] == [
        "d_mm",
        "fem_Fx_N",
        "fem_Fy_N",
        "ref_Fx_N",
        "ref_Fy_N",
        "error_ref_Fx_N",
        "error_ref_Fy_N",
    ]
    np.testing.assert_allclose(
        np.asarray(rows[1], dtype=float), [0.0, 1.0, 2.0, 0.5, 2.5, 0.5, -0.5]
    )


def test_ansys_provider_returns_nan_for_unlisted_displacement():
    assert np.isfinite(ansys_reference_force(2.0)).all()
    assert np.isnan(ansys_reference_force(3.0)).all()

