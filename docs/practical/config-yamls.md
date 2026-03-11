# Config YAML Reference

This repository now exposes one public config pair for the canonical dataset-root entrypoint:

- [configs/dataset_template.yaml](../../configs/dataset_template.yaml)
- [configs/run_conf.yaml](../../configs/run_conf.yaml)

Use them with:

```bash
python scripts/run_pipeline.py --run-config configs/run_conf.yaml --datasets-root datasets
python scripts/run_pipeline.py --run-config configs/run_conf.yaml --datasets-root datasets --validate-config
python scripts/run_pipeline.py --run-config configs/run_conf.yaml --datasets-root datasets --plan
```

## Path resolution

All relative paths in these YAML files are resolved relative to the YAML file itself, not the shell working directory.

Example:

- if `configs/run_conf.yaml` contains `datasets_root: ../datasets`
- the resolved path is relative to `configs/`

## `dataset_template.yaml`

This file controls dataset discovery defaults.

Current sections:

- `discovery`

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

## `run_conf.yaml`

This file controls the active dataset-root run.

Current top-level sections:

- `input`
- `output`
- `methodology` optional
- `sampling` optional
- `runtime` optional

### `input`

- `datasets_root`
  - required
  - root directory whose immediate child folders are treated as dataset runs

### `output`

- `results_root`
  - required
  - root directory for dataset-scoped outputs

### `methodology`

- `flow_key_fields`
  - optional
  - default directional 5-tuple
- `inactivity_timeout_seconds`
  - optional
  - default: `15`
- `size_basis`
  - optional
  - default: `packets`
- `byte_basis`
  - optional
  - default: `captured_len`

### `sampling`

- `rates`
  - optional
  - list of `X` values in `1:X`
  - `1:1` is always normalised back in as the baseline
- `method`
  - optional
  - default: `systematic`
- `random_seed`
  - optional
  - required in practice for reproducible random sampling

### `runtime`

- `plotting_mode`
  - optional
  - current supported values:
    - `minimal`
    - `off`
- `cache_policy`
  - optional
  - one of:
    - `none`
    - `minimal`
    - `debug`
- `workers`
  - optional
  - default: `1`
- `logging.level`
  - optional
  - default: `INFO`

## Current runtime behaviour

- the active entrypoint is the only public CLI surface
- the active runtime resolves one dataset-scoped executable config per dataset directory
- `cache_policy` controls hidden cache roots under `.cache/network_analysis/<policy>/`
- `none` removes dataset-scoped staged and processed cache after a successful run
- `minimal` removes only the staged cache after a successful run and keeps processed intermediates
- `debug` keeps both staged and processed cache artefacts for inspection
- the active entrypoint persists `results/<dataset>/meta/` and `results/<dataset>/logs/`
- plotting outputs are written directly under `results/<dataset>/plots/`

## Output layout

Current public outputs are dataset-scoped:

```text
results/
  <dataset_id>/
    meta/
      resolved_dataset.yaml
      run_config.yaml
      run_manifest.json
      stage_timings.json
    tables/
      <dataset_id>_metric_summary.parquet
      <dataset_id>_flow_metrics.parquet
    plots/
      ...
    logs/
      run.log
```

The active runtime also uses hidden cache roots under:

```text
.cache/
  network_analysis/
    none/
    minimal/
    debug/
```

Those cache roots are disposable and are not part of the durable public output contract.
