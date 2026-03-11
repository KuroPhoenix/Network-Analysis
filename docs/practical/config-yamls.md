# Config YAML Reference

This document explains both:

- the active post-MVP config pair used by the canonical dataset-root entrypoint; and
- the older frozen-MVP config files that still remain as compatibility interfaces.

It covers:

- active-architecture configs used by `scripts/run_pipeline.py`
- legacy single-dataset pipeline configs
- legacy batch dataset-folder configs
- field meanings
- defaults
- output layout

The current example config files are:

- [configs/dataset_template.yaml](../../configs/dataset_template.yaml)
- [configs/run_conf.yaml](../../configs/run_conf.yaml)
- [configs/pipeline.sample.yaml](../../configs/pipeline.sample.yaml)
- [configs/demo.pipeline.yaml](../../configs/demo.pipeline.yaml)
- [configs/datasets.batch.yaml](../../configs/datasets.batch.yaml)

## Active Architecture Config Pair

Use the canonical local entrypoint with:

```bash
python scripts/run_pipeline.py --run-config configs/run_conf.yaml --datasets-root datasets
python scripts/run_pipeline.py --run-config configs/run_conf.yaml --datasets-root datasets --validate-config
python scripts/run_pipeline.py --run-config configs/run_conf.yaml --datasets-root datasets --plan
```

### `dataset_template.yaml`

This file controls dataset discovery defaults.

Current fields:

- `discovery.dataset_glob`
  - optional
  - default: `*`
- `discovery.raw_glob`
  - optional
  - default: `*.pcap*`

Important behaviour:

- each immediate child folder under the datasets root is treated as one dataset unit
- direct child files matched by `raw_glob` are treated as inputs for that dataset run
- unsupported non-capture files are ignored during active run resolution

### `run_conf.yaml`

This file controls the active dataset-root run.

Current top-level sections:

- `input`
- `output`
- `methodology` optional
- `sampling` optional
- `runtime` optional

Key fields:

- `input.datasets_root`
  - required
  - root directory whose immediate child folders are treated as dataset runs
- `output.results_root`
  - required
  - root directory for dataset-scoped result outputs
- `methodology.flow_key_fields`
  - optional
  - default directional 5-tuple
- `methodology.inactivity_timeout_seconds`
  - optional
  - default: `15`
- `methodology.size_basis`
  - optional
  - default: `packets`
- `methodology.byte_basis`
  - optional
  - default: `captured_len`
- `sampling.rates`
  - optional
  - list of `X` values in `1:X`
- `sampling.method`
  - optional
  - default: `systematic`
- `sampling.random_seed`
  - optional
  - required in practice for reproducible random sampling
- `runtime.plotting_mode`
  - optional
  - current bridge values:
    - `minimal`
    - `off`
- `runtime.cache_policy`
  - optional
  - one of:
    - `none`
    - `minimal`
    - `debug`
- `runtime.workers`
  - optional
  - default: `1`
- `runtime.logging.level`
  - optional
  - default: `INFO`

Important behaviour:

- the active entrypoint still adapts into the current executable pipeline modules
- `cache_policy` is now explicit in config, but intermediate retention still follows the legacy storage model until the cache slice lands
- `results_root` is already dataset-scoped for metric tables
- the current plotting module still writes below a dataset-specific leaf inside each dataset plot root
- `meta/` and `logs/` persistence are not implemented yet

## Legacy MVP Config Surfaces

The following sections describe the older compatibility interfaces that still exist in the repo.

## Path Resolution Rule

All relative paths in these YAML files are resolved relative to the YAML file itself, not relative to the shell working directory.

Example:

- if your config is `configs/example.yaml`
- and it says `input_dir: ../datasets/demo`
- then the resolved path is relative to `configs/`

## Single-Dataset Pipeline Config

This section describes the current frozen-MVP single-dataset config shape.

Use this config type with:

```bash
python scripts/run_pipeline.py --config configs/pipeline.sample.yaml plan
python scripts/run_pipeline.py --config configs/pipeline.sample.yaml run
```

Expected top-level sections:

- `dataset`
- `output`
- `methodology` optional
- `sampling` optional
- `runtime` optional

### `dataset`

Fields:

- `dataset_id`
  - required
  - string
  - used to name processed artefacts and result files
- `input_dir`
  - required
  - directory containing raw capture files for this one dataset run
- `raw_glob`
  - optional
  - glob used to select files inside `input_dir`
  - default: `*`

Important behavior:

- all files matched by `raw_glob` are treated as part of one dataset run
- if you want one run per file, use the batch runner instead

### `output`

Fields:

- `staged_dir`
  - optional
  - default: `../data/staged`
- `processed_dir`
  - optional
  - default: `../data/processed`
- `results_tables_dir`
  - optional
  - default: `../results/tables`
- `results_plots_dir`
  - optional
  - default: `../results/plots`

Important behavior:

- staged captures are stored under `staged_dir/<dataset_id>/`
- processed intermediates are stored under `processed_dir/<dataset_id>/`
- main result tables are stored as:
  - `results_tables_dir/<dataset_id>_metric_summary.parquet`
  - `results_tables_dir/<dataset_id>_flow_metrics.parquet`
- plots are stored under `results_plots_dir/<dataset_id>/`

### `methodology`

Fields:

- `flow_key_fields`
  - optional
  - list of field names
  - default:
    - `src_ip`
    - `dst_ip`
    - `src_port`
    - `dst_port`
    - `protocol`
- `inactivity_timeout_seconds`
  - optional
  - positive integer
  - default: `15`
- `size_basis`
  - optional
  - one of:
    - `packets`
    - `bytes`
    - `both`
  - default: `packets`
- `byte_basis`
  - optional
  - currently only:
    - `captured_len`
  - default: `captured_len`

Important behavior:

- the repo default flow key is the directional 5-tuple above
- the timeout remains `15` seconds unless you override it explicitly
- `size_basis: both` makes metrics emit both packet-based and byte-based rows
- byte accounting currently uses captured packet length, not a reconstructed on-wire length

### `sampling`

Fields:

- `rates`
  - optional
  - list of positive integers expressed as `X` in `1:X`
  - default: `[1]`
- `method`
  - optional
  - one of:
    - `systematic`
    - `random`
  - default: `systematic`
- `random_seed`
  - optional at parse time
  - integer

Important behavior:

- the pipeline always normalizes rates to include the `1:1` baseline
- so if you write:
  - `rates: [10, 100]`
- the effective run set becomes:
  - `1:1, 1:10, 1:100`
- `random_seed` is required in practice when `method: random`, because the sampling module fails rather than producing non-reproducible output

### `runtime`

Fields:

- `workers`
  - optional
  - positive integer
  - default: `1`
- `enable_plots`
  - optional
  - boolean
  - default: `false`

Important behavior:

- plotting is skipped unless `enable_plots: true`
- `workers` is accepted by config validation but is not currently used to parallelize the pipeline

### Minimal Example

```yaml
dataset:
  dataset_id: my_trace
  input_dir: ../datasets/my_trace_folder
  raw_glob: "*.pcap*"

output:
  staged_dir: ../data/staged
  processed_dir: ../data/processed
  results_tables_dir: ../results/tables
  results_plots_dir: ../results/plots

methodology:
  flow_key_fields:
    - src_ip
    - dst_ip
    - src_port
    - dst_port
    - protocol
  inactivity_timeout_seconds: 15
  size_basis: packets
  byte_basis: captured_len

sampling:
  rates:
    - 2
    - 10
  method: systematic

runtime:
  enable_plots: true
```

## Batch Dataset-Folder Config

This section describes the current frozen-MVP batch config shape.

Use this config type with:

```bash
python scripts/run_dataset_batches.py --config configs/datasets.batch.yaml plan
python scripts/run_dataset_batches.py --config configs/datasets.batch.yaml run
```

Expected top-level sections:

- `discovery`
- `output`
- `methodology` optional
- `sampling` optional
- `runtime` optional

This mode is for scanning a root folder such as `datasets/`, then running the existing single-dataset pipeline once per immediate dataset folder.

### `discovery`

Fields:

- `datasets_root`
  - required
  - root directory whose immediate subfolders are treated as dataset runs
- `dataset_glob`
  - optional
  - glob for selecting dataset subfolders under `datasets_root`
  - default: `*`

Important behavior:

- only immediate subfolders under `datasets_root` are treated as dataset runs
- files belonging to one dataset should live directly inside that dataset folder
- direct child files are discovered with the batch runner's `*.pcap*` capture glob, so names such as `.pcap`, `.pcapng`, `.pcap.gz`, and `.pcap.xz` are in scope
- the whole folder is processed as one dataset
- unsupported direct child files are ignored during discovery

Example:

```text
datasets/
  bras/
    BRAS_capture_game_1.pcap
    BRAS_capture_game_2.pcap
    ...
  onu/
    ONU_capture_game_1.pcapng
    ONU_capture_game_2.pcapng
    ...
```

In this layout:

- `bras/` becomes dataset `bras`
- `onu/` becomes dataset `onu`

### `output`

Fields:

- `staged_root`
  - optional
  - default: `../data/staged`
- `processed_root`
  - optional
  - default: `../data/processed`
- `results_root`
  - optional
  - default: `../results`

Important behavior:

- each dataset folder becomes one dataset ID and one pipeline run
- processed data is stored as:
  - `data/processed/<dataset-id>/`
- results are stored as:
  - `results/<dataset-id>/tables/`
  - `results/<dataset-id>/plots/<dataset-id>/`

### `methodology`, `sampling`, and `runtime`

These sections have the same meanings as in the single-dataset config.

Additional batch behavior:

- each immediate dataset folder is run once as one dataset
- all matching capture files directly inside that folder are included in that run
- this is the right mode when you intentionally want the whole `bras/` folder treated as dataset `bras`

### Minimal Example

```yaml
discovery:
  datasets_root: ../datasets
  dataset_glob: "*"

output:
  staged_root: ../data/staged
  processed_root: ../data/processed
  results_root: ../results

methodology:
  flow_key_fields:
    - src_ip
    - dst_ip
    - src_port
    - dst_port
    - protocol
  inactivity_timeout_seconds: 15
  size_basis: packets
  byte_basis: captured_len

sampling:
  rates:
    - 10
    - 100
  method: systematic

runtime:
  enable_plots: true
```

## Practical Recommendations

- Use the single-dataset config when you want one controlled run over one capture file or one intentionally grouped file set.
- Use the batch config when you want the repo to scan `datasets/` and treat each immediate subfolder such as `datasets/bras` as one dataset.
- Keep `inactivity_timeout_seconds: 15` unless you are deliberately running a different experiment.
- Keep the flow key explicit if you ever override the default directional 5-tuple.
- Prefer `systematic` sampling first for reproducible baseline comparisons.
- If you use `random`, set `random_seed`.
- Keep raw captures immutable. Point configs at the raw folders; let the pipeline stage files itself.

## Where to Look in Code

- single-dataset config loader:
  - [config.py](../../src/network_analysis/shared/config.py)
- batch config loader:
  - [batch_config.py](../../src/network_analysis/shared/batch_config.py)
- batch execution behavior:
  - [batch_runner.py](../../src/network_analysis/batch_runner.py)
