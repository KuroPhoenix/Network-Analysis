"""Tests for dataset-folder batch planning, cleanup, and execution."""

from network_analysis.batch_runner import clean_batch_outputs, plan_batch_runs, run_batch
from network_analysis.shared.artifacts import build_artifact_paths
from network_analysis.shared.batch_config import load_batch_config


def test_plan_batch_runs_groups_by_dataset_folder(sample_batch_config_path) -> None:
    config = load_batch_config(sample_batch_config_path)

    planned_runs = plan_batch_runs(config)

    assert [(run.dataset_name, run.run_id, len(run.capture_files)) for run in planned_runs] == [
        ("Anonymized_bras_dataset", "Anonymized_bras_dataset", 2),
        ("Anonymized_onu_dataset", "Anonymized_onu_dataset", 1),
    ]

    bras_paths = build_artifact_paths(planned_runs[0].pipeline_config)
    assert bras_paths.metric_summary == (
        config.output.results_root
        / "Anonymized_bras_dataset"
        / "tables"
        / "Anonymized_bras_dataset_metric_summary.parquet"
    )


def test_run_batch_invokes_single_dataset_pipeline_per_dataset_folder(
    sample_batch_config_path,
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
        ("Anonymized_bras_dataset", "*.pcap*"),
        ("Anonymized_onu_dataset", "*.pcap*"),
    ]


def test_run_batch_emits_dataset_elapsed_time_logs(
    sample_batch_config_path,
    monkeypatch,
    capsys,
) -> None:
    config = load_batch_config(sample_batch_config_path)

    def fake_run_pipeline(pipeline_config, *, dry_run: bool = False):
        return ()

    monkeypatch.setattr("network_analysis.batch_runner.run_pipeline", fake_run_pipeline)

    run_batch(config)
    captured = capsys.readouterr()

    assert "[batch] [1/2] Anonymized_bras_dataset completed in" in captured.err
    assert "[batch] completed in" in captured.err


def test_plan_batch_runs_ignores_non_pcap_wrappers_in_dataset_folder(
    sample_batch_config_path,
) -> None:
    config = load_batch_config(sample_batch_config_path)
    zip_path = config.discovery.datasets_root / "Anonymized_bras_dataset" / "capture_bundle.zip"
    zip_path.write_text("not a capture\n", encoding="utf-8")

    planned_runs = plan_batch_runs(config)

    assert [(run.dataset_name, len(run.capture_files)) for run in planned_runs] == [
        ("Anonymized_bras_dataset", 2),
        ("Anonymized_onu_dataset", 1),
    ]


def test_clean_batch_outputs_removes_only_generated_dataset_artifacts(
    sample_batch_config_path,
) -> None:
    config = load_batch_config(sample_batch_config_path)
    planned_runs = plan_batch_runs(config)
    keep_file = config.output.results_root / "keep.me"
    keep_file.parent.mkdir(parents=True, exist_ok=True)
    keep_file.write_text("persist\n", encoding="utf-8")

    for planned_run in planned_runs:
        artifact_paths = build_artifact_paths(planned_run.pipeline_config)
        artifact_paths.staged_dir.mkdir(parents=True, exist_ok=True)
        artifact_paths.processed_dir.mkdir(parents=True, exist_ok=True)
        artifact_paths.results_tables_dir.mkdir(parents=True, exist_ok=True)
        artifact_paths.results_plots_dir.mkdir(parents=True, exist_ok=True)
        (artifact_paths.staged_dir / "staged.tmp").write_text("x\n", encoding="utf-8")
        (artifact_paths.processed_dir / "processed.tmp").write_text("x\n", encoding="utf-8")
        (artifact_paths.results_tables_dir / "summary.parquet").write_text("x\n", encoding="utf-8")
        (artifact_paths.results_plots_dir / "plot.svg").write_text("x\n", encoding="utf-8")

    cleanup_summaries = clean_batch_outputs(config)

    assert [summary.run_id for summary in cleanup_summaries] == [
        "Anonymized_bras_dataset",
        "Anonymized_onu_dataset",
    ]
    assert keep_file.exists()

    for planned_run in planned_runs:
        artifact_paths = build_artifact_paths(planned_run.pipeline_config)
        assert not artifact_paths.staged_dir.exists()
        assert not artifact_paths.processed_dir.exists()
        assert not artifact_paths.results_tables_dir.exists()
        assert not artifact_paths.results_plots_dir.exists()
