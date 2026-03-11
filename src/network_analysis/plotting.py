"""Plotting module implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .artifacts import build_artifact_paths
from .base import ModuleContract
from .config import DatasetRunConfig
from .types import ArtifactContract, ArtifactKind, ModuleName

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.PLOTTING,
    description="Render reproducible plots from computed metric tables.",
    inputs=(
        "metric summary table",
        "flow metric table",
        "plot selection",
    ),
    outputs=(
        ArtifactContract(
            name="plots",
            relative_path_template="results/{dataset_id}/plots/",
            format="svg/parquet",
            description="Static plots and plotting summary tables generated from metric tables.",
            kind=ArtifactKind.DIRECTORY,
        ),
    ),
    implemented=True,
)

_SERIES_PALETTE = (
    "#0b7285",
    "#b45309",
    "#7c3aed",
    "#15803d",
    "#c2410c",
    "#be123c",
)


@dataclass(frozen=True)
class RatePlotSpec:
    """One per-rate line-plot definition."""

    plot_key: str
    filename_suffix: str
    title: str
    metric_column: str
    y_label: str
    size_basis: str | None
    packets_preferred: bool
    aggregation_label: str


@dataclass(frozen=True)
class CdfPlotSpec:
    """One empirical-CDF plot definition."""

    plot_key: str
    filename_suffix: str
    title: str
    metric_column: str
    x_label: str
    size_basis: str | None
    packets_preferred: bool


RATE_PLOT_SPECS = (
    RatePlotSpec(
        plot_key="flow_detection_rate",
        filename_suffix="flow_detection_rate",
        title="Flow detection rate vs sampling rate",
        metric_column="flow_detection_rate",
        y_label="Flow detection rate",
        size_basis=None,
        packets_preferred=True,
        aggregation_label="direct metric-summary value",
    ),
    RatePlotSpec(
        plot_key="flow_packet_size_estimation",
        filename_suffix="flow_packet_size_estimation",
        title="Flow packet size estimation vs sampling rate",
        metric_column="sampled_size_estimate",
        y_label="Median packet size estimate",
        size_basis="packets",
        packets_preferred=False,
        aggregation_label="median over detected flows with defined sampled packet size estimates",
    ),
    RatePlotSpec(
        plot_key="flow_byte_size_estimation",
        filename_suffix="flow_byte_size_estimation",
        title="Flow byte size estimation vs sampling rate",
        metric_column="sampled_size_estimate",
        y_label="Median byte size estimate",
        size_basis="bytes",
        packets_preferred=False,
        aggregation_label="median over detected flows with defined sampled byte size estimates",
    ),
    RatePlotSpec(
        plot_key="flow_duration_estimation",
        filename_suffix="flow_duration_estimation",
        title="Flow duration vs sampling rate",
        metric_column="sampled_duration_seconds",
        y_label="Median sampled duration (s)",
        size_basis=None,
        packets_preferred=True,
        aggregation_label="median over detected flows with defined sampled durations",
    ),
    RatePlotSpec(
        plot_key="flow_packet_sending_rate",
        filename_suffix="flow_packet_sending_rate",
        title="Flow packet sending rate vs sampling rate",
        metric_column="sampled_sending_rate",
        y_label="Median packet sending rate",
        size_basis="packets",
        packets_preferred=False,
        aggregation_label="median over detected flows with defined sampled packet sending rates",
    ),
    RatePlotSpec(
        plot_key="flow_byte_sending_rate",
        filename_suffix="flow_byte_sending_rate",
        title="Flow byte sending rate vs sampling rate",
        metric_column="sampled_sending_rate",
        y_label="Median byte sending rate",
        size_basis="bytes",
        packets_preferred=False,
        aggregation_label="median over detected flows with defined sampled byte sending rates",
    ),
)

CDF_PLOT_SPECS = (
    CdfPlotSpec(
        plot_key="flow_packet_size_overestimation_factor",
        filename_suffix="flow_packet_size_overestimation_factor_cdf",
        title="Flow packet size overestimation factor CDF",
        metric_column="flow_size_overestimation_factor",
        x_label="Packet size overestimation factor",
        size_basis="packets",
        packets_preferred=False,
    ),
    CdfPlotSpec(
        plot_key="flow_byte_size_overestimation_factor",
        filename_suffix="flow_byte_size_overestimation_factor_cdf",
        title="Flow byte size overestimation factor CDF",
        metric_column="flow_size_overestimation_factor",
        x_label="Byte size overestimation factor",
        size_basis="bytes",
        packets_preferred=False,
    ),
    CdfPlotSpec(
        plot_key="flow_duration_underestimation_factor",
        filename_suffix="flow_duration_underestimation_factor_cdf",
        title="Flow duration underestimation factor CDF",
        metric_column="flow_duration_underestimation_factor",
        x_label="Duration underestimation factor",
        size_basis=None,
        packets_preferred=True,
    ),
    CdfPlotSpec(
        plot_key="flow_byte_sending_rate_overestimation_factor",
        filename_suffix="flow_byte_sending_rate_overestimation_factor_cdf",
        title="Flow byte sending rate overestimation factor CDF",
        metric_column="flow_sending_rate_overestimation_factor",
        x_label="Byte sending rate overestimation factor",
        size_basis="bytes",
        packets_preferred=False,
    ),
    CdfPlotSpec(
        plot_key="flow_packet_sending_rate_overestimation_factor",
        filename_suffix="flow_packet_sending_rate_overestimation_factor_cdf",
        title="Flow packet sending rate overestimation factor CDF",
        metric_column="flow_sending_rate_overestimation_factor",
        x_label="Packet sending rate overestimation factor",
        size_basis="packets",
        packets_preferred=False,
    ),
)


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


def run_module(config: DatasetRunConfig) -> Path:
    """Render lightweight static plots from metric tables."""

    import polars as pl

    artifact_paths = build_artifact_paths(config)
    if not artifact_paths.metric_summary.exists():
        raise FileNotFoundError(
            f"Metric summary table is missing. Run {ModuleName.METRICS} first: {artifact_paths.metric_summary}"
        )
    if not artifact_paths.flow_metrics.exists():
        raise FileNotFoundError(
            f"Flow metric table is missing. Run {ModuleName.METRICS} first: {artifact_paths.flow_metrics}"
        )

    metric_summary = pl.read_parquet(artifact_paths.metric_summary)
    flow_metrics = pl.read_parquet(artifact_paths.flow_metrics)
    if metric_summary.is_empty():
        raise ValueError("Plotting found an empty metric summary table.")
    if flow_metrics.is_empty():
        raise ValueError("Plotting found an empty flow metric table.")

    artifact_paths.plots_dir.mkdir(parents=True, exist_ok=True)
    plotting_summary_rows: list[dict[str, object]] = []

    detection_rows = _select_detection_rate_rows(metric_summary)
    _write_text(
        artifact_paths.plots_dir / f"{config.dataset.dataset_id}_flow_detection_rate.svg",
        _render_rate_line_svg(
            title=RATE_PLOT_SPECS[0].title,
            subtitle=(
                f"Dataset {config.dataset.dataset_id} | baseline flows {int(detection_rows[0]['baseline_flow_count'])} "
                f"| source metric metric_summary.flow_detection_rate"
            ),
            rows=detection_rows,
            y_label=RATE_PLOT_SPECS[0].y_label,
            value_formatter=_format_decimal,
            fixed_y_max=1.0,
        ),
    )
    plotting_summary_rows.extend(
        _build_summary_rows(
            config=config,
            spec=RATE_PLOT_SPECS[0],
            rows=detection_rows,
            source_metric="metric_summary.flow_detection_rate",
        )
    )

    for spec in RATE_PLOT_SPECS[1:]:
        rows = _build_rate_plot_rows(flow_metrics, spec)
        if not rows:
            continue
        size_basis_note = (
            f" | size basis {rows[0]['size_basis']}"
            if rows[0]["size_basis"] is not None
            else ""
        )
        _write_text(
            artifact_paths.plots_dir / f"{config.dataset.dataset_id}_{spec.filename_suffix}.svg",
            _render_rate_line_svg(
                title=spec.title,
                subtitle=(
                    f"Dataset {config.dataset.dataset_id}{size_basis_note} | "
                    f"{spec.aggregation_label}"
                ),
                rows=rows,
                y_label=spec.y_label,
                value_formatter=_format_numeric,
                fixed_y_max=None,
            ),
        )
        plotting_summary_rows.extend(
            _build_summary_rows(
                config=config,
                spec=spec,
                rows=rows,
                source_metric=f"flow_metrics.{spec.metric_column}",
            )
        )

    for spec in CDF_PLOT_SPECS:
        series = _build_cdf_series(flow_metrics, spec)
        if not series:
            continue
        _write_text(
            artifact_paths.plots_dir / f"{config.dataset.dataset_id}_{spec.filename_suffix}.svg",
            _render_cdf_svg(
                title=spec.title,
                subtitle=(
                    f"Dataset {config.dataset.dataset_id} | "
                    f"defined detected-flow rows from flow_metrics.{spec.metric_column}"
                ),
                x_label=spec.x_label,
                series=series,
            ),
        )

    if plotting_summary_rows:
        pl.DataFrame(plotting_summary_rows).sort(["plot_key", "sampling_rate"]).write_parquet(
            artifact_paths.plotting_summary
        )

    return artifact_paths.plots_dir


def _select_detection_rate_rows(metric_summary):
    import polars as pl

    summary = metric_summary.sort(["sampling_rate", "size_basis"])
    packets_only = summary.filter(pl.col("size_basis") == "packets")
    if not packets_only.is_empty():
        summary = packets_only

    return summary.unique(subset=["sampling_rate"], keep="first").sort("sampling_rate").to_dicts()


def _build_rate_plot_rows(flow_metrics, spec: RatePlotSpec) -> list[dict[str, object]]:
    import polars as pl

    selected = _select_flow_metric_rows(flow_metrics, size_basis=spec.size_basis, packets_preferred=spec.packets_preferred)
    if selected.is_empty():
        return []

    filtered = selected.filter(
        (pl.col("detection_status") == "detected")
        & pl.col(spec.metric_column).is_not_null()
    )
    if filtered.is_empty():
        return []

    return (
        filtered.group_by(["dataset_id", "sampling_rate", "size_basis", "byte_basis"])
        .agg(
            pl.len().alias("defined_flow_count"),
            pl.col(spec.metric_column).median().alias("plotted_value"),
        )
        .sort("sampling_rate")
        .to_dicts()
    )


def _build_cdf_series(flow_metrics, spec: CdfPlotSpec) -> list[dict[str, object]]:
    import polars as pl

    selected = _select_flow_metric_rows(flow_metrics, size_basis=spec.size_basis, packets_preferred=spec.packets_preferred)
    if selected.is_empty():
        return []

    filtered = selected.filter(
        (pl.col("detection_status") == "detected")
        & pl.col(spec.metric_column).is_not_null()
    )
    if filtered.is_empty():
        return []

    series: list[dict[str, object]] = []
    for row in (
        filtered.group_by("sampling_rate")
        .agg(pl.col(spec.metric_column).sort().alias("values"))
        .sort("sampling_rate")
        .iter_rows(named=True)
    ):
        values = [float(value) for value in row["values"]]
        point_rows = []
        for index, value in enumerate(values, start=1):
            point_rows.append(
                {
                    "x_value": value,
                    "y_value": index / len(values),
                }
            )
        series.append(
            {
                "label": f"1:{int(row['sampling_rate'])}",
                "sampling_rate": int(row["sampling_rate"]),
                "points": point_rows,
            }
        )
    return series


def _select_flow_metric_rows(flow_metrics, *, size_basis: str | None, packets_preferred: bool):
    import polars as pl

    if size_basis is not None:
        return flow_metrics.filter(pl.col("size_basis") == size_basis)

    if not packets_preferred:
        return flow_metrics

    packets_only = flow_metrics.filter(pl.col("size_basis") == "packets")
    if not packets_only.is_empty():
        return packets_only
    return flow_metrics


def _build_summary_rows(
    *,
    config: DatasetRunConfig,
    spec: RatePlotSpec,
    rows: list[dict[str, object]],
    source_metric: str,
) -> list[dict[str, object]]:
    summary_rows: list[dict[str, object]] = []
    for row in rows:
        summary_rows.append(
            {
                "dataset_id": config.dataset.dataset_id,
                "plot_key": spec.plot_key,
                "plot_title": spec.title,
                "sampling_rate": int(row["sampling_rate"]),
                "size_basis": row.get("size_basis"),
                "byte_basis": row.get("byte_basis"),
                "aggregation": spec.aggregation_label,
                "source_metric": source_metric,
                "plotted_value": float(row["plotted_value"] if "plotted_value" in row else row["flow_detection_rate"]),
                "defined_flow_count": (
                    int(row["defined_flow_count"])
                    if row.get("defined_flow_count") is not None
                    else int(row["baseline_flow_count"])
                ),
            }
        )
    return summary_rows


def _render_rate_line_svg(
    *,
    title: str,
    subtitle: str,
    rows: list[dict[str, object]],
    y_label: str,
    value_formatter,
    fixed_y_max: float | None,
) -> str:
    width = 920
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
    y_values = [
        float(row["plotted_value"] if "plotted_value" in row else row["flow_detection_rate"])
        for row in rows
    ]
    y_max = fixed_y_max if fixed_y_max is not None else max(y_values)
    if y_max <= 0:
        y_max = 1.0
    y_max *= 1.05 if fixed_y_max is None else 1.0

    def x_for_index(index: int) -> float:
        if len(rows) == 1:
            return x_start + plot_width / 2
        return x_start + (plot_width * index / (len(rows) - 1))

    def y_for_value(value: float) -> float:
        return y_start - (plot_height * value / y_max)

    point_coordinates = [
        (x_for_index(index), y_for_value(value))
        for index, value in enumerate(y_values)
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
        value = y_max * step / 5
        y = y_for_value(value)
        y_ticks.append(
            f'<line x1="{x_start - 8}" y1="{y:.2f}" x2="{x_start}" y2="{y:.2f}" stroke="#333" stroke-width="1" />'
        )
        y_ticks.append(
            f'<line x1="{x_start}" y1="{y:.2f}" x2="{x_start + plot_width}" y2="{y:.2f}" stroke="#d9d9d9" stroke-width="1" />'
        )
        y_ticks.append(
            f'<text x="{x_start - 16}" y="{y + 6:.2f}" text-anchor="end" font-size="15" fill="#222">{value_formatter(value)}</text>'
        )

    point_marks = []
    for (x, y), rate, plotted_value in zip(point_coordinates, sampling_rates, y_values, strict=True):
        point_marks.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="#0b7285" stroke="#083344" stroke-width="2" />'
        )
        point_marks.append(
            f'<text x="{x:.2f}" y="{y - 14:.2f}" text-anchor="middle" font-size="14" fill="#083344">{value_formatter(plotted_value)}</text>'
        )
        if rate == 1:
            point_marks.append(
                f'<text x="{x:.2f}" y="{y + 28:.2f}" text-anchor="middle" font-size="13" fill="#555">ground truth baseline</text>'
            )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{subtitle}</desc>
  <rect width="{width}" height="{height}" fill="#f8f6f1" />
  <text x="{x_start}" y="42" font-size="28" font-weight="700" fill="#111">{title}</text>
  <text x="{x_start}" y="68" font-size="16" fill="#444">{subtitle}</text>
  <line x1="{x_start}" y1="{y_start}" x2="{x_start + plot_width}" y2="{y_start}" stroke="#222" stroke-width="2" />
  <line x1="{x_start}" y1="{margin_top}" x2="{x_start}" y2="{y_start}" stroke="#222" stroke-width="2" />
  {''.join(y_ticks)}
  {''.join(x_ticks)}
  <polyline fill="none" stroke="#0b7285" stroke-width="4" points="{polyline_points}" />
  {''.join(point_marks)}
  <text x="{x_start + plot_width / 2:.2f}" y="{height - 28}" text-anchor="middle" font-size="18" fill="#222">Sampling rate (1:X)</text>
  <text x="24" y="{margin_top + plot_height / 2:.2f}" transform="rotate(-90 24 {margin_top + plot_height / 2:.2f})" text-anchor="middle" font-size="18" fill="#222">{y_label}</text>
</svg>
"""


def _render_cdf_svg(
    *,
    title: str,
    subtitle: str,
    x_label: str,
    series: list[dict[str, object]],
) -> str:
    width = 940
    height = 600
    margin_left = 90
    margin_right = 150
    margin_top = 90
    margin_bottom = 90
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    x_start = margin_left
    y_start = height - margin_bottom

    x_values = [
        point["x_value"]
        for item in series
        for point in item["points"]
    ]
    x_min = min(x_values)
    x_max = max(x_values)
    if x_min == x_max:
        padding = 0.5 if x_min == 0 else abs(x_min) * 0.1
        x_min -= padding
        x_max += padding

    def x_for_value(value: float) -> float:
        return x_start + plot_width * ((value - x_min) / (x_max - x_min))

    def y_for_probability(value: float) -> float:
        return y_start - plot_height * value

    y_ticks = []
    for step in range(6):
        value = step / 5
        y = y_for_probability(value)
        y_ticks.append(
            f'<line x1="{x_start - 8}" y1="{y:.2f}" x2="{x_start}" y2="{y:.2f}" stroke="#333" stroke-width="1" />'
        )
        y_ticks.append(
            f'<line x1="{x_start}" y1="{y:.2f}" x2="{x_start + plot_width}" y2="{y:.2f}" stroke="#d9d9d9" stroke-width="1" />'
        )
        y_ticks.append(
            f'<text x="{x_start - 16}" y="{y + 6:.2f}" text-anchor="end" font-size="15" fill="#222">{value:.1f}</text>'
        )

    x_ticks = []
    for step in range(6):
        value = x_min + ((x_max - x_min) * step / 5)
        x = x_for_value(value)
        x_ticks.append(
            f'<line x1="{x:.2f}" y1="{y_start}" x2="{x:.2f}" y2="{y_start + 8}" stroke="#333" stroke-width="1" />'
        )
        x_ticks.append(
            f'<text x="{x:.2f}" y="{y_start + 28}" text-anchor="middle" font-size="16" fill="#222">{_format_numeric(value)}</text>'
        )

    polylines = []
    legend_items = []
    for index, item in enumerate(series):
        color = _SERIES_PALETTE[index % len(_SERIES_PALETTE)]
        points = " ".join(
            f"{x_for_value(point['x_value']):.2f},{y_for_probability(point['y_value']):.2f}"
            for point in item["points"]
        )
        polylines.append(
            f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{points}" />'
        )
        legend_y = margin_top + 24 + (index * 24)
        legend_items.append(
            f'<line x1="{width - 132}" y1="{legend_y}" x2="{width - 104}" y2="{legend_y}" stroke="{color}" stroke-width="3" />'
        )
        legend_items.append(
            f'<text x="{width - 96}" y="{legend_y + 5}" font-size="14" fill="#222">{item["label"]}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{subtitle}</desc>
  <rect width="{width}" height="{height}" fill="#f8f6f1" />
  <text x="{x_start}" y="42" font-size="28" font-weight="700" fill="#111">{title}</text>
  <text x="{x_start}" y="68" font-size="16" fill="#444">{subtitle}</text>
  <line x1="{x_start}" y1="{y_start}" x2="{x_start + plot_width}" y2="{y_start}" stroke="#222" stroke-width="2" />
  <line x1="{x_start}" y1="{margin_top}" x2="{x_start}" y2="{y_start}" stroke="#222" stroke-width="2" />
  {''.join(y_ticks)}
  {''.join(x_ticks)}
  {''.join(polylines)}
  {''.join(legend_items)}
  <text x="{x_start + plot_width / 2:.2f}" y="{height - 28}" text-anchor="middle" font-size="18" fill="#222">{x_label}</text>
  <text x="24" y="{margin_top + plot_height / 2:.2f}" transform="rotate(-90 24 {margin_top + plot_height / 2:.2f})" text-anchor="middle" font-size="18" fill="#222">Empirical CDF</text>
</svg>
"""


def _format_decimal(value: float) -> str:
    return f"{value:.2f}"


def _format_numeric(value: float) -> str:
    if value == 0:
        return "0"
    magnitude = abs(value)
    if magnitude >= 10_000 or magnitude < 0.01:
        return f"{value:.2e}"
    if magnitude >= 100:
        return f"{value:.0f}"
    if magnitude >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
