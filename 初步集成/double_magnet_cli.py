"""Command-line interface for the modular double-magnet benchmark."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
from typing import Callable, Sequence

from comparison import ForceComparison, compare_force_results
from double_magnet_reference import akoun_yonnet_force, ansys_reference_force


@dataclass(frozen=True)
class DoubleMagnetCLIOptions:
    """Validated command-line configuration for one benchmark run."""

    displacements_mm: tuple[float, ...]
    degree: int
    h_near_mm: float
    h_far_mm: float
    show_mesh: bool
    compare: bool
    csv_path: str | None
    force_plot_path: str | None
    error_plot_path: str | None
    show_comparison: bool

    @property
    def comparison_requested(self) -> bool:
        return any(
            (
                self.compare,
                self.csv_path,
                self.force_plot_path,
                self.error_plot_path,
                self.show_comparison,
            )
        )


def build_parser() -> argparse.ArgumentParser:
    """Create the benchmark argument parser without reading ``sys.argv``."""
    parser = argparse.ArgumentParser(
        description="Modular FEALPy double-magnet scalar-potential benchmark"
    )

    solve_group = parser.add_argument_group("finite-element solve")
    solve_group.add_argument(
        "--d",
        type=float,
        nargs="+",
        default=[0.0],
        metavar="MM",
        help="one or more x-displacements in mm, for example --d 0 2 4",
    )
    solve_group.add_argument(
        "--p", type=int, default=2, help="continuous Lagrange degree (default: 2)"
    )
    solve_group.add_argument(
        "--h-near",
        type=float,
        default=1.5,
        metavar="MM",
        help="near-field target mesh size in mm (default: 1.5)",
    )
    solve_group.add_argument(
        "--h-far",
        type=float,
        default=6.0,
        metavar="MM",
        help="far-field target mesh size in mm (default: 6.0)",
    )

    display_group = parser.add_argument_group("interactive display")
    display_group.add_argument(
        "--show", action="store_true", help="open the Gmsh mesh window"
    )
    display_group.add_argument(
        "--show-comparison",
        action="store_true",
        help="display the force comparison plot interactively",
    )

    comparison_group = parser.add_argument_group("comparison outputs")
    comparison_group.add_argument(
        "--compare",
        action="store_true",
        help="print F1 comparisons with analytical and ANSYS references",
    )
    comparison_group.add_argument(
        "--csv", metavar="PATH", help="write comparison cases to a CSV file"
    )
    comparison_group.add_argument(
        "--plot", metavar="PATH", help="save a force comparison plot"
    )
    comparison_group.add_argument(
        "--error-plot",
        metavar="PATH",
        help="save a signed-error plot (FEALPy minus each reference)",
    )
    return parser


def parse_cli_args(argv: Sequence[str] | None = None) -> DoubleMagnetCLIOptions:
    """Parse and validate command-line arguments."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.p < 1:
        parser.error("--p must be at least 1")
    if any(not math.isfinite(value) or value < 0.0 for value in args.d):
        parser.error("--d values must be finite and non-negative")
    if not math.isfinite(args.h_near) or args.h_near <= 0.0:
        parser.error("--h-near must be finite and positive")
    if not math.isfinite(args.h_far) or args.h_far <= 0.0:
        parser.error("--h-far must be finite and positive")
    if args.h_near > args.h_far:
        parser.error("--h-near must not exceed --h-far")

    return DoubleMagnetCLIOptions(
        displacements_mm=tuple(args.d),
        degree=args.p,
        h_near_mm=args.h_near,
        h_far_mm=args.h_far,
        show_mesh=args.show,
        compare=args.compare,
        csv_path=args.csv,
        force_plot_path=args.plot,
        error_plot_path=args.error_plot,
        show_comparison=args.show_comparison,
    )


def print_force_results(results) -> None:
    """Print the force convention and one force pair per displacement."""
    print("Force convention: F0=lower magnet, F1=upper magnet=-F0")
    for result in results:
        print(f'd={result["d"]:g} mm')
        print("  F0 (lower magnet):", result["F0"], "N")
        print("  F1 (upper magnet):", result["F1"], "N")


def process_comparison(
    results, options: DoubleMagnetCLIOptions
) -> ForceComparison | None:
    """Build requested reports and return the comparison for further use."""
    if not options.comparison_requested:
        return None

    comparison = compare_force_results(
        results,
        references={
            "analytic": akoun_yonnet_force,
            "ANSYS": ansys_reference_force,
        },
        force_key="F1",
    )
    if options.compare:
        print("\nForce comparison (F1, upper magnet)")
        print(comparison.format_cases())
    print("\nError metrics")
    print(comparison.format_metrics())

    if options.csv_path:
        print("Comparison CSV:", comparison.write_csv(options.csv_path))
    if options.force_plot_path or options.show_comparison:
        comparison.plot(
            options.force_plot_path, show=options.show_comparison
        )
        if options.force_plot_path:
            print("Comparison plot:", options.force_plot_path)
    if options.error_plot_path:
        comparison.plot_errors(options.error_plot_path)
        print("Error plot:", options.error_plot_path)
    return comparison


def run_from_options(
    options: DoubleMagnetCLIOptions,
    solve_many: Callable,
):
    """Execute the benchmark using an injected batch-solve function."""
    results = solve_many(
        options.displacements_mm,
        p=options.degree,
        h_near_mm=options.h_near_mm,
        h_far_mm=options.h_far_mm,
        show=options.show_mesh,
    )
    print_force_results(results)
    process_comparison(results, options)
    return results


def main(argv: Sequence[str] | None = None) -> None:
    """Allow this CLI module to be executed directly as well."""
    options = parse_cli_args(argv)

    from fealpy.backend import backend_manager as bm

    from modular_double_magnet_benchmark import solve_many

    bm.set_backend("numpy")
    run_from_options(options, solve_many)


if __name__ == "__main__":
    main()
