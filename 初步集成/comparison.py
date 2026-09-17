"""Generic comparison, reporting, CSV export and plotting for force curves."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import operator
from pathlib import Path
from typing import Callable, Mapping

import numpy as np


ReferenceProvider = Callable[[float], object] | Mapping[float, object]


@dataclass(frozen=True)
class ComponentMetrics:
    count: int
    mae: float
    rmse: float
    max_abs_error: float
    max_error_d: float
    normalized_rmse: float


@dataclass
class ForceComparison:
    displacements: np.ndarray
    numerical: np.ndarray
    references: dict[str, np.ndarray]
    component_names: tuple[str, ...]
    force_key: str

    @property
    def errors(self) -> dict[str, np.ndarray]:
        return {
            name: self.numerical - values
            for name, values in self.references.items()
        }

    def metrics(self) -> dict[str, dict[str, ComponentMetrics]]:
        result: dict[str, dict[str, ComponentMetrics]] = {}
        for reference_name, reference in self.references.items():
            error = self.numerical - reference
            result[reference_name] = {}
            for index, component in enumerate(self.component_names):
                valid = np.isfinite(reference[:, index]) & np.isfinite(error[:, index])
                if not np.any(valid):
                    result[reference_name][component] = ComponentMetrics(
                        0, np.nan, np.nan, np.nan, np.nan, np.nan
                    )
                    continue
                component_error = error[valid, index]
                component_d = self.displacements[valid]
                absolute = np.abs(component_error)
                maximum_index = int(np.argmax(absolute))
                rmse = float(np.sqrt(np.mean(component_error**2)))
                scale = float(np.max(np.abs(reference[valid, index])))
                normalized_rmse = rmse / scale if scale > 0.0 else np.nan
                result[reference_name][component] = ComponentMetrics(
                    count=int(np.count_nonzero(valid)),
                    mae=float(np.mean(absolute)),
                    rmse=rmse,
                    max_abs_error=float(absolute[maximum_index]),
                    max_error_d=float(component_d[maximum_index]),
                    normalized_rmse=normalized_rmse,
                )
        return result

    def format_cases(self) -> str:
        columns = ["d/mm"]
        columns.extend(f"FEM_{name}/N" for name in self.component_names)
        for reference_name in self.references:
            columns.extend(
                f"{reference_name}_{name}/N" for name in self.component_names
            )
            columns.extend(
                f"error_{reference_name}_{name}/N" for name in self.component_names
            )
        lines = ["  ".join(f"{column:>20}" for column in columns)]
        errors = self.errors
        for row, displacement in enumerate(self.displacements):
            values = [f"{displacement:.6g}"]
            values.extend(f"{value:.8g}" for value in self.numerical[row])
            for name, reference in self.references.items():
                values.extend(f"{value:.8g}" for value in reference[row])
                values.extend(f"{value:.8g}" for value in errors[name][row])
            lines.append("  ".join(f"{value:>20}" for value in values))
        return "\n".join(lines)

    def format_metrics(self) -> str:
        lines = []
        for reference_name, components in self.metrics().items():
            lines.append(f"Reference: {reference_name}")
            lines.append(
                "  component  count       MAE/N      RMSE/N   "
                "max|error|/N  at d/mm  normalized RMSE"
            )
            for component, metric in components.items():
                lines.append(
                    f"  {component:>9}  {metric.count:5d}  "
                    f"{metric.mae:10.4e}  {metric.rmse:10.4e}  "
                    f"{metric.max_abs_error:12.4e}  "
                    f"{metric.max_error_d:7.3g}  {metric.normalized_rmse:15.4e}"
                )
        return "\n".join(lines)

    def write_csv(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        header = ["d_mm"]
        header.extend(f"fem_{name}_N" for name in self.component_names)
        for reference_name in self.references:
            header.extend(
                f"{reference_name}_{name}_N" for name in self.component_names
            )
            header.extend(
                f"error_{reference_name}_{name}_N"
                for name in self.component_names
            )
        errors = self.errors
        with output.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            for row, displacement in enumerate(self.displacements):
                values = [displacement, *self.numerical[row]]
                for name, reference in self.references.items():
                    values.extend(reference[row])
                    values.extend(errors[name][row])
                writer.writerow(values)
        return output

    def plot(self, path: str | Path | None = None, show: bool = False):
        import matplotlib.pyplot as plt

        component_count = len(self.component_names)
        figure, axes = plt.subplots(
            component_count, 1, figsize=(8, 3.5 * component_count), squeeze=False
        )
        for index, component in enumerate(self.component_names):
            axis = axes[index, 0]
            axis.plot(
                self.displacements,
                self.numerical[:, index],
                "o-",
                label=f"FEALPy {component}",
            )
            for name, reference in self.references.items():
                axis.plot(
                    self.displacements,
                    reference[:, index],
                    "s--",
                    label=f"{name} {component}",
                )
            axis.set_xlabel("Displacement d (mm)")
            axis.set_ylabel(f"Force {component} (N)")
            axis.grid(True)
            axis.legend()
        figure.tight_layout()
        if path is not None:
            output = Path(path)
            output.parent.mkdir(parents=True, exist_ok=True)
            figure.savefig(output, dpi=180, bbox_inches="tight")
        if show:
            plt.show()
        else:
            plt.close(figure)
        return figure

    def plot_errors(self, path: str | Path | None = None, show: bool = False):
        """Plot signed errors ``numerical - reference`` for every component."""
        import matplotlib.pyplot as plt

        component_count = len(self.component_names)
        figure, axes = plt.subplots(
            component_count, 1, figsize=(8, 3.5 * component_count), squeeze=False
        )
        errors = self.errors
        for index, component in enumerate(self.component_names):
            axis = axes[index, 0]
            axis.axhline(0.0, color="black", linewidth=0.8)
            for name, error in errors.items():
                valid = np.isfinite(error[:, index])
                axis.plot(
                    self.displacements[valid],
                    error[valid, index],
                    "o-",
                    label=f"FEALPy - {name}",
                )
            axis.set_xlabel("Displacement d (mm)")
            axis.set_ylabel(f"{component} error (N)")
            axis.grid(True)
            axis.legend()
        figure.tight_layout()
        if path is not None:
            output = Path(path)
            output.parent.mkdir(parents=True, exist_ok=True)
            figure.savefig(output, dpi=180, bbox_inches="tight")
        if show:
            plt.show()
        else:
            plt.close(figure)
        return figure


def _reference_value(provider: ReferenceProvider, displacement: float):
    if callable(provider):
        return provider(displacement)
    return provider.get(float(displacement), None)


def compare_force_results(
    results,
    references: Mapping[str, ReferenceProvider],
    force_key: str = "F1",
    components: tuple[int, ...] = (0, 1),
    component_names: tuple[str, ...] = ("Fx", "Fy"),
) -> ForceComparison:
    """Compare force entries in solver results with one or more references."""
    if not results:
        raise ValueError("at least one numerical result is required")
    if not isinstance(references, Mapping) or not references:
        raise ValueError("at least one reference provider is required")
    if not components:
        raise ValueError("at least one force component is required")
    try:
        components = tuple(operator.index(value) for value in components)
    except TypeError as exc:
        raise TypeError("components must contain integers") from exc
    if len(set(components)) != len(components):
        raise ValueError("components must not contain duplicate indices")
    if any(index < 0 for index in components):
        raise ValueError("components must contain non-negative indices")

    component_names = tuple(str(name) for name in component_names)
    if len(components) != len(component_names):
        raise ValueError("components and component_names must have equal lengths")
    if any(not name for name in component_names):
        raise ValueError("component_names must not contain empty names")
    if len(set(component_names)) != len(component_names):
        raise ValueError("component_names must be unique")

    displacements = np.asarray(
        [float(result["d"]) for result in results],
        dtype=float,
    )
    if not np.isfinite(displacements).all():
        raise ValueError("numerical displacements must be finite")
    rows = []
    for result in results:
        vector = np.asarray(result[force_key], dtype=float)
        if vector.ndim != 1 or max(components) >= vector.size:
            raise ValueError(
                f"each {force_key!r} value must be a vector containing all "
                "selected components"
            )
        rows.append(vector[list(components)])
    numerical = np.asarray(rows, dtype=float)
    if not np.isfinite(numerical).all():
        raise ValueError("numerical force values must be finite")

    reference_arrays: dict[str, np.ndarray] = {}
    for raw_name, provider in references.items():
        name = str(raw_name)
        if not name:
            raise ValueError("reference names must not be empty")
        if name in reference_arrays:
            raise ValueError(f"duplicate reference name after conversion: {name!r}")
        if not callable(provider) and not isinstance(provider, Mapping):
            raise TypeError("each reference provider must be callable or a mapping")
        rows = []
        for displacement in displacements:
            value = _reference_value(provider, float(displacement))
            if value is None:
                rows.append(np.full(len(components), np.nan))
            else:
                vector = np.asarray(value, dtype=float)
                if vector.ndim != 1:
                    raise ValueError(
                        f"reference {name!r} values must be one-dimensional"
                    )
                if np.isinf(vector).any():
                    raise ValueError(
                        f"reference {name!r} values must not contain infinity"
                    )
                # Two-component reference providers already mean (Fx, Fy).
                if vector.size == len(components):
                    rows.append(vector.reshape(-1))
                else:
                    if max(components) >= vector.size:
                        raise ValueError(
                            f"reference {name!r} does not contain all selected "
                            "components"
                        )
                    rows.append(vector[list(components)])
        reference_arrays[name] = np.asarray(rows, dtype=float)
    return ForceComparison(
        displacements=displacements,
        numerical=numerical,
        references=reference_arrays,
        component_names=component_names,
        force_key=force_key,
    )
