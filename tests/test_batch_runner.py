"""Tests for dataset-folder batch planning and execution."""

from pathlib import Path

from network_analysis.batch_runner import plan_batch_runs, run_batch
from network_analysis.shared.artifacts import build_artifact_paths
from network_analysis.shared.batch_config import load_batch_config


def test_plan_batch_runs_groups_by_dataset_and_category(sample_batch_config_path: Path) -> None:
    config = load_batch_config(sample_batch_config_path)

    planned_runs = plan_batch_runs(config)

    assert [(run.dataset_name, run.category, run.run_id) for run in planned_runs] == [
        ("Anonymized_bras_dataset", "game", "BRAS_capture_game_1"),
        ("Anonymized_bras_dataset", "video", "BRAS_capture_video_2"),
        ("Anonymized_onu_dataset", "uncategorized", "misc_trace"),
    ]

    bras_game_paths = build_artifact_paths(planned_runs[0].pipeline_config)
    assert bras_game_paths.metric_summary == (
        config.output.results_root
        / "Anonymized_bras_dataset"
        / "game"
        / "tables"
        / "BRAS_capture_game_1_metric_summary.parquet"
    )


def test_run_batch_invokes_single_dataset_pipeline_per_capture(
    sample_batch_config_path: Path,
    monkeypatch,
) -> None:
    config = load_batch_config(sample_batch_config_path)
    calls: list[tuple[str, str]] = []

    def fake_run_pipeline(pipeline_config, *, dry_run: bool = False):
        calls.append((pipeline_config.dataset.dataset_id, pipeline_config.dataset.raw_glob))
        return ()

    monkeypatch.setattr("network_analysis.batch_runner.run_pipeline", fake_run_pipeline)

    run_batch(config)

    assert calls == [
        ("BRAS_capture_game_1", "BRAS_capture_game_1.pcap"),
        ("BRAS_capture_video_2", "BRAS_capture_video_2.pcap"),
        ("misc_trace", "misc_trace.pcapng"),
    ]
