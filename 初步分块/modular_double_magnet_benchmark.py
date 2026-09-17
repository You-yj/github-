#!/usr/bin/env python3
"""Double-magnet benchmark assembled from reusable magnetostatic modules."""

from __future__ import annotations

import argparse
import math

import numpy as np

from fealpy.backend import backend_manager as bm

from comparison import compare_force_results
from double_magnet_reference import (
    akoun_yonnet_force,
    ansys_reference_force,
)
from magnetostatic import (
    Air,
    BoxRegion,
    GeometryModel,
    GmshTetraMesher,
    MaxwellStressPostprocessor,
    MeshOptions,
    PermanentMagnet,
    ScalarPotentialPDE,
    ScalarPotentialSolver,
)
from magnetostatic.geometry import BoxSizeField


MU0 = 4.0 * math.pi * 1.0e-7
BR_Z = 0.38
MZ = BR_Z / MU0


def make_geometry(displacement_mm: float) -> GeometryModel:
    """Build the original benchmark geometry using SI units.

    All boxes use :meth:`BoxRegion.from_corners` with the exact corner
    arithmetic of the original program, so the generated mesh reproduces
    the reference mesh bit for bit (no center/size round-trip ulp drift).
    """
    d = float(displacement_mm)
    x_max_mm = 30.0 + max(d - 8.0, 0.0)
    outer_lower = np.array([-30.0, -30.0, -27.0]) * 1.0e-3
    outer_upper = np.array([x_max_mm, 30.0, 27.0]) * 1.0e-3
    maxwell_lower = np.array([-12.0, -8.0, -5.0]) * 1.0e-3
    maxwell_upper = np.array([12.0, 8.0, 4.0]) * 1.0e-3

    return GeometryModel(
        outer=BoxRegion.from_corners("outer_air", outer_lower, outer_upper),
        regions=(
            BoxRegion.from_corners(
                "maxwell_air", maxwell_lower, maxwell_upper, priority=0
            ),
            BoxRegion.from_corners(
                "lower_magnet",
                np.array([-10.0, -6.0, -3.0]) * 1.0e-3,
                np.array([10.0, 6.0, 3.0]) * 1.0e-3,
                priority=10,
            ),
            BoxRegion.from_corners(
                "upper_magnet",
                np.array([-10.0 + d, -14.0, 5.0]) * 1.0e-3,
                np.array([2.0 + d, 6.0, 11.0]) * 1.0e-3,
                priority=10,
            ),
        ),
        interface_names={
            "lower_magnet_maxwell_surface": ("maxwell_air", "outer_air")
        },
    )


def make_mesh_options(
    displacement_mm: float,
    h_near_mm: float = 1.5,
    h_far_mm: float = 6.0,
    show: bool = False,
) -> MeshOptions:
    d = float(displacement_mm)
    size_field = BoxSizeField(
        lower=np.array([-18.0, -20.0, -11.0]) * 1.0e-3,
        upper=np.array([max(18.0, d + 8.0), 14.0, 17.0]) * 1.0e-3,
        h_inside=h_near_mm * 1.0e-3,
        h_outside=h_far_mm * 1.0e-3,
        thickness=8.0e-3,
    )
    return MeshOptions(size_fields=(size_field,), show=show)


def make_pde() -> ScalarPotentialPDE:
    magnet = PermanentMagnet(magnetization=[0.0, 0.0, MZ])
    return ScalarPotentialPDE(
        {
            "outer_air": Air(),
            "maxwell_air": Air(),
            "lower_magnet": magnet,
            "upper_magnet": magnet,
        },
        mu0=MU0,
    )


def solve(
    displacement_mm: float,
    p: int = 2,
    h_near_mm: float = 1.5,
    h_far_mm: float = 6.0,
    show: bool = False,
):
    geometry = make_geometry(displacement_mm)
    mesh_data = GmshTetraMesher().generate(
        geometry,
        make_mesh_options(displacement_mm, h_near_mm, h_far_mm, show),
        model_name=f"double_magnet_d{displacement_mm:g}",
    )
    solution = ScalarPotentialSolver(p=p).solve(mesh_data, make_pde())
    lower_force = MaxwellStressPostprocessor().compute_force(
        solution, "lower_magnet_maxwell_surface"
    )
    return {
        "d": float(displacement_mm),
        "solution": solution,
        "phi": solution.potential,
        "F0": lower_force,
        "F1": -lower_force,
    }


def solve_many(
    displacements_mm,
    p: int = 2,
    h_near_mm: float = 1.5,
    h_far_mm: float = 6.0,
    show: bool = False,
):
    """Solve several displacement cases and return one result per value of d."""
    return [
        solve(d, p, h_near_mm, h_far_mm, show)
        for d in displacements_mm
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--d",
        type=float,
        nargs="+",
        default=[0.0],
        metavar="MM",
        help="one or more x-displacements in mm, for example --d 0 2 4",
    )
    parser.add_argument("--p", type=int, default=2)
    parser.add_argument("--h-near", type=float, default=1.5)
    parser.add_argument("--h-far", type=float, default=6.0)
    parser.add_argument("--show", action="store_true")
    parser.add_argument(
        "--compare",
        action="store_true",
        help="compare upper-magnet F1 with analytical and ANSYS references",
    )
    parser.add_argument("--csv", help="write comparison cases to a CSV file")
    parser.add_argument("--plot", help="save a force comparison plot")
    parser.add_argument(
        "--error-plot",
        help="save a signed-error plot (FEALPy minus each reference)",
    )
    parser.add_argument(
        "--show-comparison",
        action="store_true",
        help="display the force comparison plot interactively",
    )
    args = parser.parse_args()
    bm.set_backend("numpy")
    results = solve_many(
        args.d, args.p, args.h_near, args.h_far, args.show
    )
    for result in results:
        print(f'd={result["d"]:g} mm')
        print("  F0 (lower magnet):", result["F0"], "N")
        print("  F1 (upper magnet):", result["F1"], "N")

    comparison_requested = any(
        (
            args.compare,
            args.csv,
            args.plot,
            args.error_plot,
            args.show_comparison,
        )
    )
    if comparison_requested:
        comparison = compare_force_results(
            results,
            references={
                "analytic": akoun_yonnet_force,
                "ANSYS": ansys_reference_force,
            },
            force_key="F1",
        )
        if args.compare:
            print("\nForce comparison (F1, upper magnet)")
            print(comparison.format_cases())
        print("\nError metrics")
        print(comparison.format_metrics())
        if args.csv:
            print("Comparison CSV:", comparison.write_csv(args.csv))
        if args.plot or args.show_comparison:
            comparison.plot(args.plot, show=args.show_comparison)
            if args.plot:
                print("Comparison plot:", args.plot)
        if args.error_plot:
            comparison.plot_errors(args.error_plot)
            print("Error plot:", args.error_plot)


if __name__ == "__main__":
    main()
