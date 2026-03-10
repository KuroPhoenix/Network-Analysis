"""Plotting module implementation."""

from pathlib import Path

from .base import ModuleContract
from ..shared.artifacts import build_artifact_paths
from ..shared.config import PipelineConfig
from ..shared.types import ArtifactContract, ArtifactKind, ModuleName

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.PLOTTING,
    description="Render minimal reproducible plots from computed metric tables.",
    inputs=(
        "metric summary table",
        "flow metric table",
        "plot selection",
    ),
    outputs=(
        ArtifactContract(
            name="plots",
            relative_path_template="results/plots/{dataset_id}/",
            format="svg",
            description="Static plots generated from metric tables.",
            kind=ArtifactKind.DIRECTORY,
        ),
    ),
    implemented=True,
)


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


def run_module(config: PipelineConfig) -> Path:
    """Render lightweight static plots from metric tables."""

    import polars as pl

    artifact_paths = build_artifact_paths(config)
    if not artifact_paths.metric_summary.exists():
        raise FileNotFoundError(
            f"Metric summary table is missing. Run {ModuleName.METRICS} first: {artifact_paths.metric_summary}"
        )

    metric_summary = pl.read_parquet(artifact_paths.metric_summary)
    if metric_summary.is_empty():
        raise ValueError("Plotting found an empty metric summary table.")

    plot_rows = _select_detection_rate_rows(metric_summary)
    artifact_paths.plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = artifact_paths.plots_dir / f"{config.dataset.dataset_id}_flow_detection_rate.svg"
    output_path.write_text(
        _render_detection_rate_svg(config=config, rows=plot_rows),
        encoding="utf-8",
    )
    return output_path


def _select_detection_rate_rows(metric_summary):
    import polars as pl

    summary = metric_summary.sort(["sampling_rate", "size_basis"])
    packets_only = summary.filter(pl.col("size_basis") == "packets")
    if not packets_only.is_empty():
        summary = packets_only

    return summary.unique(subset=["sampling_rate"], keep="first").sort("sampling_rate").to_dicts()


def _render_detection_rate_svg(*, config: PipelineConfig, rows: list[dict[str, object]]) -> str:
    width = 900
    height = 560
    margin_left = 90
    margin_right = 40
    margin_top = 90
    margin_bottom = 90
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    x_start = margin_left
    y_start = height - margin_bottom

    sampling_rates = [int(row["sampling_rate"]) for row in rows]
    detection_rates = [float(row["flow_detection_rate"]) for row in rows]
    baseline_flow_count = int(rows[0]["baseline_flow_count"])
    size_basis = str(rows[0]["size_basis"])
    byte_basis = str(rows[0]["byte_basis"])

    def x_for_index(index: int) -> float:
        if len(rows) == 1:
            return x_start + plot_width / 2
        return x_start + (plot_width * index / (len(rows) - 1))

    def y_for_rate(rate: float) -> float:
        return y_start - (plot_height * rate)

    point_coordinates = [
        (x_for_index(index), y_for_rate(rate))
        for index, rate in enumerate(detection_rates)
    ]
    polyline_points = " ".join(f"{x:.2f},{y:.2f}" for x, y in point_coordinates)

    x_ticks = []
    for index, rate in enumerate(sampling_rates):
        x = x_for_index(index)
        x_ticks.append(
            f'<line x1="{x:.2f}" y1="{y_start}" x2="{x:.2f}" y2="{y_start + 8}" stroke="#333" stroke-width="1" />'
        )
        x_ticks.append(
            f'<text x="{x:.2f}" y="{y_start + 28}" text-anchor="middle" font-size="16" fill="#222">1:{rate}</text>'
        )

    y_ticks = []
    for step in range(6):
        value = step / 5
        y = y_for_rate(value)
        y_ticks.append(
            f'<line x1="{x_start - 8}" y1="{y:.2f}" x2="{x_start}" y2="{y:.2f}" stroke="#333" stroke-width="1" />'
        )
        y_ticks.append(
            f'<line x1="{x_start}" y1="{y:.2f}" x2="{x_start + plot_width}" y2="{y:.2f}" stroke="#d9d9d9" stroke-width="1" />'
        )
        y_ticks.append(
            f'<text x="{x_start - 16}" y="{y + 6:.2f}" text-anchor="end" font-size="15" fill="#222">{value:.1f}</text>'
        )

    point_marks = []
    for (x, y), rate, detection_rate in zip(point_coordinates, sampling_rates, detection_rates, strict=True):
        point_marks.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="#0b7285" stroke="#083344" stroke-width="2" />'
        )
        point_marks.append(
            f'<text x="{x:.2f}" y="{y - 14:.2f}" text-anchor="middle" font-size="14" fill="#083344">{detection_rate:.2f}</text>'
        )
        if rate == 1:
            point_marks.append(
                f'<text x="{x:.2f}" y="{y + 28:.2f}" text-anchor="middle" font-size="13" fill="#555">ground truth baseline</text>'
            )

    subtitle = (
        f"Dataset {config.dataset.dataset_id} | baseline flows {baseline_flow_count} | "
        f"size basis {size_basis} | byte basis {byte_basis}"
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Flow detection rate vs sampling rate</title>
  <desc id="desc">Detection rate for each 1:X sampling rate compared directly against the 1:1 baseline.</desc>
  <rect width="{width}" height="{height}" fill="#f8f6f1" />
  <text x="{x_start}" y="42" font-size="28" font-weight="700" fill="#111">Flow detection rate vs sampling rate</text>
  <text x="{x_start}" y="68" font-size="16" fill="#444">{subtitle}</text>
  <line x1="{x_start}" y1="{y_start}" x2="{x_start + plot_width}" y2="{y_start}" stroke="#222" stroke-width="2" />
  <line x1="{x_start}" y1="{margin_top}" x2="{x_start}" y2="{y_start}" stroke="#222" stroke-width="2" />
  {''.join(y_ticks)}
  {''.join(x_ticks)}
  <polyline fill="none" stroke="#0b7285" stroke-width="4" points="{polyline_points}" />
  {''.join(point_marks)}
  <text x="{x_start + plot_width / 2:.2f}" y="{height - 28}" text-anchor="middle" font-size="18" fill="#222">Sampling rate (1:X)</text>
  <text x="24" y="{margin_top + plot_height / 2:.2f}" transform="rotate(-90 24 {margin_top + plot_height / 2:.2f})" text-anchor="middle" font-size="18" fill="#222">Flow detection rate</text>
</svg>
"""
