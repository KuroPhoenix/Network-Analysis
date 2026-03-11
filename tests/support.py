"""Helpers for building active-architecture test configs."""

from __future__ import annotations

from pathlib import Path

from network_analysis.config import (
    DatasetConfig,
    DatasetRunConfig,
    OutputConfig,
    load_run_config,
)


def build_dataset_run_config(
    tmp_path: Path,
    *,
    dataset_id: str = "fixture_trace",
    raw_glob: str = "*.pcap",
    sampling_rates: tuple[int, ...] = (2,),
    plotting_mode: str = "off",
    size_basis: str = "packets",
    byte_basis: str = "captured_len",
    cache_policy: str = "debug",
) -> DatasetRunConfig:
    """Build one active per-dataset config for unit tests."""

    datasets_root = tmp_path / "datasets"
    dataset_dir = datasets_root / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    dataset_template_path = tmp_path / "dataset_template.yaml"
    dataset_template_path.write_text(
        f"""
discovery:
  dataset_glob: "{dataset_id}"
  raw_glob: "{raw_glob}"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    rates_yaml = "\n".join(f"    - {rate}" for rate in sampling_rates)
    run_config_path = tmp_path / "run_conf.yaml"
    run_config_path.write_text(
        f"""
input:
  datasets_root: ./datasets

output:
  results_root: ./results

methodology:
  flow_key_fields:
    - src_ip
    - dst_ip
    - src_port
    - dst_port
    - protocol
  inactivity_timeout_seconds: 15
  size_basis: {size_basis}
  byte_basis: {byte_basis}

sampling:
  rates:
{rates_yaml}
  method: systematic

runtime:
  workers: 1
  plotting_mode: {plotting_mode}
  cache_policy: {cache_policy}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    run_config = load_run_config(run_config_path)
    cache_root = tmp_path / ".cache" / "network_analysis" / cache_policy
    return DatasetRunConfig(
        config_path=run_config.config_path,
        dataset=DatasetConfig(
            dataset_id=dataset_id,
            input_dir=dataset_dir,
            raw_glob=raw_glob,
        ),
        output=OutputConfig(
            staged_dir=cache_root / "staged",
            processed_dir=cache_root / "processed",
            results_tables_dir=tmp_path / "results" / dataset_id / "tables",
            results_plots_dir=tmp_path / "results" / dataset_id / "plots",
        ),
        methodology=run_config.methodology,
        sampling=run_config.sampling,
        runtime=run_config.runtime,
    )
