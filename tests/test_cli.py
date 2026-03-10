"""Tests for the thin CLI and driver skeleton."""

from pathlib import Path

from network_analysis.cli import main
from network_analysis.pipeline.driver import get_stage_catalog


def test_stage_catalog_uses_named_stage_modules() -> None:
    stage_names = [stage.name for stage in get_stage_catalog()]

    assert stage_names == [
        "dataset_registry",
        "ingest",
        "packet_extraction",
        "flow_construction",
        "sampling",
        "metrics",
        "plotting",
    ]


def test_cli_validate_config_reports_defaults(sample_config_path: Path, capsys) -> None:
    exit_code = main(["--config", str(sample_config_path), "validate-config"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Dataset: fixture_trace" in captured.out
    assert "Inactivity timeout: 15s" in captured.out
    assert "Sampling rates: 1:1, 1:10, 1:100" in captured.out


def test_cli_plan_prints_stage_sequence(sample_config_path: Path, capsys) -> None:
    exit_code = main(["--config", str(sample_config_path), "plan"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "dataset_registry" in captured.out
    assert "packet_extraction" in captured.out
    assert "results/tables/fixture_trace_metric_summary.parquet" in captured.out

