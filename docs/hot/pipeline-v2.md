# Pipeline Active Specification

## Purpose

This document defines the active post-MVP architecture for the local-first packet-trace analysis pipeline in this repository.

It preserves the repo’s research contract:

1. ingest real packet-capture datasets;
2. reconstruct unsampled ground-truth flows;
3. reconstruct sampled flows under one or more `1:X` packet-sampling conditions;
4. measure how sampling affects flow detection and flow-level metrics; and
5. emit inspectable outputs and reproducible analysis figures.

This document does **not** replace the frozen MVP methodology.
It refines the implementation architecture, execution model, storage model, and repo layout while preserving the established analysis contract.

If current architecture or module implementation conflicts with this file, treat `pipeline-v2.md` as the authoritative target architecture and update the repo accordingly.

---

## Document status and naming

### Lifecycle rule

This file is the **active** architecture spec.

Recommended naming scheme:

- `docs/frozen/pipeline-mvp.md` = frozen validated MVP baseline
- `docs/hot/pipeline-v2.md` = current evolving implementation target

Do not create `v2`, `v3`, or numeric source-tree duplicates such as `src_v2/`.
Version labels belong to architecture milestones and frozen documents, not parallel code trees.

### Authority rule

Unless explicitly overridden:

- `AGENTS.md` defines repo-wide operating rules, methodology constraints, review discipline, and default working style.
- this document defines the current implementation architecture and execution model;
- module documentation under `docs/modules/<module>/` explains the implemented behaviour and maintenance details of each exposed module;
- skills guide workflow patterns and do not override methodology or architecture.

If these documents conflict, surface the conflict explicitly and resolve it instead of silently choosing one interpretation.

---

## Design principles

### 1. Ground-truth first
Always process the unsampled full trace first.
The `1:1` case is the only ground-truth baseline.
Every sampled `1:X` result must be compared directly against that baseline.

### 2. Preserve methodology, refine architecture
Post-MVP work may simplify the repo, reduce storage cost, improve logging (If possible, use existing python packages such as loguru), and add safe parallelism, but it must not silently redefine:
- the baseline rule;
- the timeout rule;
- the default flow key;
- metric formulas;
- dataset acceptance expectations;
- unit semantics.

### 3. Single clear entrypoint
The repo should expose one obvious local command that discovers datasets, resolves per-dataset configs, runs the pipeline, and writes dataset-scoped outputs.

### 4. Dataset-scoped execution
Each dataset should be processed as an isolated unit:
- build one `1:1` baseline for that dataset;
- evaluate one or more `1:X` conditions against that baseline;
- write outputs under `results/<dataset_id>/...`

### 5. Thin orchestration
The runnable entrypoint and runtime layer should compose modules, manage run state, and write manifests.
They must not hide methodology or contain core metric logic.

### 6. Resource-aware local execution
The default execution model should be stable on a single local machine with limited memory.
Peak RAM use matters more than elegant but memory-heavy architecture.

### 7. Persistent outputs over persistent intermediates
Final tables, plots, manifests, and logs should be persisted.
Heavy packet-scale intermediates should be persisted only when explicitly enabled by cache policy.

### 8. Parquet over CSV
Do not use raw CSV as the primary intermediate representation for packet-scale data.
Prefer Parquet for structured packet, flow, and metric artefacts.

### 9. Explicit configuration
Timeout, flow key, sampling rates, size basis, byte basis, dataset identity, plotting mode, cache policy, and execution options must stay visible in config or manifests, not hidden in code.

### 10. Documentation stays disciplined
Keep module documentation and change tracking, but do not let architecture docs sprawl.
Use:
- one frozen baseline spec;
- one active architecture spec;
- module documentation only for implemented module boundaries.

Git history is the default routine changelog for implementation work.
Manual doc updates are for current architecture, methodology, config or output contracts, milestone state, and material maintenance guidance.

Keep module `CHANGELOG.md` files, but reserve them for purpose-, architecture-, direction-, or milestone-driven notes rather than routine code churn.

---

## Scope of the active architecture

The active architecture covers these conceptual modules:

1. dataset discovery and config resolution
2. ingest and optional staging
3. packet extraction to canonical packet table
4. baseline flow construction
5. sampling emulation or sampled reconstruction
6. metric computation against baseline
7. plotting and report outputs
8. runtime/orchestration, logging, and manifests

The following remain out of scope unless explicitly requested:

- Kubernetes integration
- distributed execution
- production deployment packaging
- broad benchmarking for publication
- GPU-only execution paths
- interactive UI layers

---

## Current implementation gaps vs target architecture

The current repository is directionally aligned with this active architecture, but it has not fully converged yet.

Known gaps to treat as active refactor targets:

- the canonical local entrypoint is already defined by this document as `python scripts/run_pipeline.py --datasets-root datasets --run-config configs/run_conf.yaml`; if the current repo does not yet provide that behavior cleanly, create or adapt a thin entrypoint to do so rather than introducing more parallel wrappers;
- the target `configs/dataset_template.yaml` plus `configs/run_conf.yaml` split now exists as scaffolding, but the canonical execution path still centers on legacy sample and batch configs until the single-entrypoint migration is complete;
- persistent `data/raw/`, `data/staged/`, and `data/processed/` trees are still used in the live implementation rather than a fully cache-policy-driven disposable storage model;
- dataset-scoped `results/<dataset_id>/tables/` and `plots/` are already in use, but `results/<dataset_id>/meta/` and `results/<dataset_id>/logs/` are not yet first-class persisted outputs;
- runtime visibility currently appears mainly in terminal progress and elapsed-time output; persisted logs, run manifests, and resolved dataset snapshots are not yet fully implemented;
- plotting is still partial: the current implementation renders the flow-detection-rate figure, but not the full plot family described later in this document;
- the Python package layout still uses `modules/`, `pipeline/`, and `shared/` boundaries rather than the flatter target layout shown in this document.

These gaps are implementation gaps, not methodology gaps.
Until they are closed, preserve the current validated behaviour while moving the codebase toward the target architecture incrementally.

### Legacy replacement rule

When a legacy wrapper, config surface, or user-facing document is superseded by this active architecture, update, retire, or clearly mark it as legacy in the same change set.

Do not leave frozen-MVP and target-v2 interfaces presented as equally current without explicit labelling.

---

## Input model

### Dataset root

The default input layout is:

```text
datasets/
  A-trace/
    ...
  B-trace/
    ...
````

Each immediate child folder under `datasets/` is treated as one dataset unit unless explicitly configured otherwise.

### Accepted inputs

The pipeline should accept packet captures in:

* `pcap`
* `pcapng`

Compressed wrappers may also be accepted when explicitly supported, such as:

* `.gz`
* `.xz`
* `.zip`
* `.rar` only if support is deliberately added and documented

When capture bytes are directly readable, format detection should prefer header inspection over filename suffixes.

### Dataset requirements

The intended research workflow assumes:

* full-trace packet capture data;
* not already sampled traces as the source baseline;
* capture year preferably `2020+`;
* `2024–2026` preferred when available;
* accurate per-packet timestamps;
* preferably documented lossless capture;
* preferably documented full wire-format packet data.

The implementation must preserve and report uncertainty when these properties are incompletely documented.

---

## Configuration model

The active architecture uses two top-level config files:

```text
configs/
  dataset_template.yaml
  run_conf.yaml
```

### `dataset_template.yaml`

This file provides:

* dataset config schema;
* required fields;
* default assumptions;
* discovery rules;
* validation rules;
* optional override fields.

It is a read-only template and must **not** be mutated in place during execution.

### `run_conf.yaml`

This file provides run-level controls:

* sampling rate list;
* sampling method;
* inactivity timeout;
* flow key override if any;
* size basis;
* byte basis;
* plotting mode;
* cache policy;
* worker count or parallelism limit;
* logging configuration;
* enabled modules or partial-run controls when supported.

### Resolved dataset config rule

For each discovered dataset:

1. read `dataset_template.yaml`;
2. infer dataset-specific values from the dataset folder;
3. merge template defaults, discovered fields, and explicit overrides;
4. validate the resolved config;
5. keep the resolved config in memory during execution;
6. persist a snapshot under `results/<dataset_id>/meta/resolved_dataset.yaml`
7. if the current config setup conflicts with this file, an immediate modification is required.
Do **not** rewrite the shared template file on disk for each dataset.

---

## Execution model

### Single entrypoint

The pipeline should expose one clear local entrypoint, for example:

```text
python scripts/run_pipeline.py --datasets-root datasets --run-config configs/run_conf.yaml
```
This is the canonical local entrypoint for the active architecture.
If the current repository does not already expose a command that satisfies this contract, create a new thin entrypoint rather than extending the ambiguity between legacy wrappers.

The entrypoint can be a shell file or a Python file.

### Execution order

For each discovered dataset:

1. resolve dataset config
2. validate dataset and discover usable capture files
3. ingest or stage capture inputs if needed
4. extract canonical packet table
5. construct `1:1` baseline flows
6. execute each configured `1:X` sampling condition
7. compute metrics against the shared baseline
8. generate requested plots
9. write manifests, logs, and result snapshots

### Output layout

Outputs should be dataset-scoped:

```text
results/
  A-trace/
    meta/
    tables/
    plots/
    logs/
  B-trace/
    meta/
    tables/
    plots/
    logs/
```

This layout is preferred over mixing outputs from different datasets into a single global tables directory.

---

## Storage and cache policy

### Persistent areas

Persistent outputs should include:

* resolved config snapshots
* manifests
* summary tables
* per-flow metric tables
* plots
* logs
* small reproducible exports

### Default storage simplification

A large always-on `data/raw/`, `data/staged/`, `data/processed/` tree is **not** required in the active architecture.

Instead:

* `datasets/` is the input root;
* `results/` holds persistent analysis artefacts;
* optional cache or temp storage is disposable.

### Cache policy

The run config should expose:

* `none`
* `minimal`
* `debug`

Meaning:

* `none`: keep only final outputs and manifests
* `minimal`: keep only artefacts that avoid expensive recomputation
* `debug`: keep packet-scale and flow-scale intermediates for inspection

If a cache directory is used, it should be clearly disposable and outside normal Git tracking.

---

## Methodology specification

### Baseline rule

The `1:1` full-trace reconstruction is the only ground-truth baseline.

### Sampling rule

Each `1:X` condition is evaluated as a sampled approximation.
Every sampled result must be compared directly against the `1:1` baseline, not against another sampled rate.

### Flow continuity rule

Use a default inactivity timeout of **15 seconds** unless explicitly overridden in configuration.

Interpretation:

* packet gaps of **15 seconds or less** remain within the same flow record;
* packet gaps **greater than 15 seconds** terminate the current flow and start a new one.

### Flow key rule

The default flow key is the directional 5-tuple:

* source IP
* destination IP
* source port
* destination port
* protocol

If a dataset or task requires a different flow key, the override must be explicit and recorded in manifests and outputs.

### Size basis rule

The pipeline must keep the size basis explicit:

* `packets`
* `bytes`


Do not mix packet-based and byte-based metrics without explicit labels.

### Reporting rule for expected effects

The repo may expect directional sampling effects, but these are expected trends, not universal laws.
The code and reports must compute and report measured outcomes rather than forcing predetermined conclusions.

---

## Metric definitions

The active architecture must preserve these flow-level metrics.

### Baseline metrics (`1:1`)

* **Flow byte size** = total byte count observed in the reconstructed baseline flow
* **Flow packet size** = total packet count observed in the reconstructed baseline flow
* **Flow duration** = `last_packet_timestamp - first_packet_timestamp`
* **Flow byte sending rate** = `flow byte size / flow duration`
* **Flow packet sending rate** = `flow packet size / flow duration`
* **Flow detection rate** = `100%`

### Sampled metrics (`1:X`)

* **Sampled flow packet size estimate** = sampled packet count in the reconstructed sampled flow × sampling rate, unless another estimator is explicitly chosen
* **Sampled flow byte size estimate** = sampled byte total in the reconstructed sampled flow × sampling rate, unless another estimator is explicitly chosen
* **Sampled flow duration** = `last_sampled_packet_timestamp - first_sampled_packet_timestamp` within the sampled reconstruction only
* **Sampled flow packet sending rate** = `sampled flow packet size estimate / sampled flow duration`
* **Sampled flow byte sending rate** = `sampled flow byte size estimate / sampled flow duration`
* **Flow detection rate** = `detected baseline flows / total baseline flows`

### Derived distortion metrics

* **Flow packet size overestimation factor** = `sampled packet size estimate / actual baseline packet size`
* **Flow byte size overestimation factor** = `sampled byte size estimate / actual baseline byte size`
* **Flow duration underestimation factor** = `sampled flow duration / actual baseline flow duration`
* **Flow byte sending rate overestimation factor** = `flow byte size overestimation factor / flow duration underestimation factor`
* **Flow packet sending rate overestimation factor** = `flow packet size overestimation factor / flow duration underestimation factor`

### Undefined cases

If a denominator is zero, the metric must remain explicitly undefined, such as `NA`, `null`, or another clearly documented non-numeric value.

This applies especially to:

* zero-duration flows;
* rates derived from zero-duration flows;
* ratio metrics whose denominator is zero.

Undefined values should remain explicit in stored outputs.
Downstream summary calculations and plots may filter undefined rows only for the specific metric being aggregated, and that filtering rule must be documented.

Undetected flows must remain visible in completeness accounting and must not be silently dropped from flow-detection denominators.

---

## Architecture model

The preferred conceptual flow is:

`dataset folder -> resolved dataset config -> packet extraction -> baseline flows -> sampled flows / sampled observations -> baseline-aligned metrics -> plots`

The preferred physical implementation may simplify adjacent modules, but exposed contracts must remain explicit.

For example:

* `flow_construction` and `sampling` may remain separate modules, or
* they may sit under one physical `flows` package,
  as long as the baseline and sampled responsibilities remain clear and separately testable.

---

## Module-by-module specification

## Module 1: Dataset discovery and config resolution

### Purpose

Discover dataset folders under the configured dataset root, infer capture inputs, validate basic usability, and resolve one dataset config per dataset without mutating the shared template.

### Inputs

* `datasets/` root
* `dataset_template.yaml`
* `run_conf.yaml`
* optional dataset-level overrides

### Outputs

Under `results/<dataset_id>/meta/`:

* `resolved_dataset.yaml`
* `dataset_manifest.parquet` or equivalent structured manifest
* dataset discovery metadata sufficient for downstream provenance

### Rules

* dataset discovery must be deterministic;
* each dataset folder maps to one dataset identifier unless explicitly overridden;
* file detection should report uncertainty rather than silently guessing;
* full-trace suitability and provenance caveats should remain visible.

### Validation

* deterministic folder discovery
* deterministic file ordering
* resolved config validation
* explicit failure on unsupported or unreadable inputs

---

## Module 2: Ingest and optional staging

### Purpose

Prepare readable capture inputs for parsing while preserving raw dataset files as immutable inputs.

### Inputs

* resolved dataset config
* discovered input files
* optional cache policy

### Outputs

* readable capture files or staged paths
* ingest manifest under `results/<dataset_id>/meta/`
* optional cached staged files when cache policy allows

### Rules

* raw inputs remain immutable;
* staging is optional, not mandatory;
* decompression must be explicit and reproducible;
* header-based format detection is preferred when bytes are readable.

### Validation

* readable staged paths when staging is needed
* deterministic staging actions
* explicit failure on unsupported wrappers or unreadable members

---

## Module 3: Packet extraction

### Purpose

Convert each usable capture into a canonical packet table suitable for baseline reconstruction and sampling analysis.

### Inputs

* usable `pcap` or `pcapng` inputs
* parser config
* resolved dataset config

### Required packet fields

At minimum:

* `dataset_id`
* `packet_index`
* `packet_size`
* `timestamp`
* `protocol`
* `src_ip`
* `dst_ip`
* `src_port`
* `dst_port`

Optional fields may be added if documented.

### Outputs

Depending on cache policy:

* in-memory packet table;
* optional persisted packet table under cache or debug outputs;
* packet extraction manifest under `results/<dataset_id>/meta/`

### Rules

* preserve packet order semantics;
* keep timestamp fidelity intact;
* fail loudly if flow-reconstruction-critical fields cannot be derived;
* prefer Parquet if packet tables are persisted.

### Validation

* schema contract checks
* tiny capture extraction
* capture-order determinism
* header-based format detection success for mislabeled but valid inputs

---

## Module 4: Ground-truth flow construction

### Purpose

Reconstruct directional flow records from the unsampled packet table.

### Inputs

* canonical packet table
* explicit or default flow key
* inactivity timeout, default `15s`

### Outputs

At minimum, baseline flow data containing:

* `dataset_id`
* `flow_id`
* flow-key fields
* `start_ts`
* `end_ts`
* `duration`
* `packet_count`
* `byte_count`
* `sending_rate_packets`
* `sending_rate_bytes`
* explicit unit and byte-basis labels

These may be persisted under cache or debug policy and must be reflected in downstream metadata.

### Rules

* use the directional 5-tuple by default unless overridden;
* use the configured inactivity timeout consistently;
* single-packet flows are valid;
* deterministic input must produce deterministic flow reconstruction.

### Validation

* timeout splitting at exactly `15s`
* timeout splitting when gap is greater than `15s`
* single-packet flow handling
* deterministic reconstruction on a known tiny fixture

---

## Module 5: Sampling emulation or sampled reconstruction

### Purpose

Produce sampled packet observations and sampled flow reconstructions under one or more `1:X` packet-sampling conditions.

### Inputs

* canonical packet table or baseline-compatible packet source
* one or more sampling rates
* one explicit sampling procedure

### Outputs

At minimum:

* sampling manifest
* sampled summaries per rate
* optional sampled packet and sampled flow artefacts when cache policy permits

### Rules

* do not treat an externally supplied sampled trace as ground truth;
* if external sampled traces are accepted, their provenance relative to the full trace must be explicit;
* sampled flows must be reconstructed from sampled packets only;
* do not scale full baseline flows directly.

### Validation

* `1:1` behaves as the no-loss reference path
* at least one `1:X` path runs successfully
* sampling settings and seeds are recorded explicitly
* sampled outputs remain consumable by metric computation

---

## Module 6: Metric computation

### Purpose

Match sampled observations to baseline flows and compute completeness and distortion metrics.

### Inputs

* baseline flow data
* sampled outputs or sampled packet tables
* flow key definition
* timeout configuration
* size basis
* byte basis

### Outputs

Under `results/<dataset_id>/tables/` at minimum:

* summary table per sampled rate
* per-flow metric table
* optional compact exports for plotting

### Rules

* compare every sampled result directly against the `1:1` baseline;
* keep undetected flows in the detection denominator;
* do not silently drop undetected flows;
* label packet-based and byte-based outputs explicitly;
* keep undefined metric values explicit.

### Validation

* sampled-vs-baseline matching correctness
* detection denominator correctness
* metric formulas consistent with repo definitions
* zero-duration handling explicit and test-covered

---

## Module 7: Plotting

### Purpose

Produce reproducible visual outputs from computed metrics.

### Plot families

* flow detection rate under different sampling rates (1:1 inclusive)
* flow packet count estimation under different sampling rates (1:1 inclusive)
* flow byte size estimation under different sampling rates (1:1 inclusive)
* flow duration under different sampling rates (1:1 inclusive)
* flow packet sending rate under different sampling rates (1:1 inclusive)
* flow byte size sending rate under different sampling rates (1:1 inclusive)

### Inputs

* metric tables
* plotting mode from run config

### Outputs

Under `results/<dataset_id>/plots/`:

* static figures
* optional plotting summary tables
* **Flow packet size overestimation factor**
* **Flow byte size overestimation factor**
* **Flow duration underestimation factor**
* **Flow byte sending rate overestimation factor**
* **Flow packet sending rate overestimation factor**

### Rules

* plotting is downstream of metrics and must not change metric semantics;
* labels must make dataset, baseline condition, sampling rate, and unit basis clear.

### Validation

* all plot renders for a small dataset
* plotted values correspond to stored metric outputs
* Other outputs aligns with the plot results and the computation results
---

## Module 8: Runtime, logging, and manifests

### Purpose

Provide thin orchestration, run-state management, lightweight execution visibility, and reproducibility metadata.

### Inputs

* resolved run config
* resolved dataset config
* module contracts

### Outputs

Under `results/<dataset_id>/meta/` and `results/<dataset_id>/logs/`:

* run manifest
* config snapshots
* stage timings
* log files
* failure summaries when relevant

### Rules

* runtime remains thin;
* methodology logic remains in modules;
* logging must not change pipeline semantics;
* every run should have one clear run identifier.

### Validation

* one tiny end-to-end run succeeds
* stage order is visible
* outputs are written to predictable locations
* elapsed times and failure summaries are inspectable

### Runtime exposure
Keep the logs in the specified folder as mentioned above. However, for clarity, expose the following information to the user in the terminal:
1. The module which the code is now processing
2. Tqdm progress bar to show the progress of the current module


---

## Recommended repository layout

```text
project/
  configs/
    dataset_template.yaml
    run_conf.yaml
  datasets/
    A-trace/
    B-trace/
  docs/
    frozen/
      pipeline-mvp.md
    hot/
      pipeline-v2.md
  docs/modules/
    <module-name>/
      README.md
      CHANGELOG.md
      Maintenance.md
  results/
    <dataset_id>/
      meta/
      tables/
      plots/
      logs/
  scripts/
    run_pipeline.py
  src/
    <package_name>/
      cli.py
      runtime.py
      logging.py
      config.py
      dataset_registry.py
      ingest.py
      packets.py
      flows.py
      metrics.py
      plotting.py
      artifacts.py
  tests/
```

The exact physical file layout may vary, but the architecture should preserve the distinction between:

* dataset inputs
* reproducibility metadata
* results
* reusable source code
* tests
* module documentation
* active vs frozen architecture specs

---

## Review and documentation requirements

### Review principles

Changes must be reviewed against:

* baseline integrity
* timeout integrity
* flow-key stability
* metric-definition consistency
* explicit unit labelling
* reproducibility
* memory-safety impact
* logging or runtime changes that might obscure methodology

### Documentation principles

For each implemented module, maintain:

* `README.md`
* `CHANGELOG.md`
* `Maintenance.md`

These must stay aligned with:

* purpose
* inputs and outputs
* schemas or contracts
* assumptions
* limitations
* upstream/downstream integration
* known maintenance issues

Routine implementation history should be tracked through Git branches, commits, and merge or pull-request descriptions.

Do not use module `CHANGELOG.md` files for routine implementation churn.
Use them for purpose-, architecture-, direction-, interface-, or milestone-driven notes that Git history alone would not explain clearly enough.

### Architecture-doc principle

Do not create sprawling architecture subtrees.
Use:

* one frozen baseline spec
* one active architecture spec
* module docs only where the module boundary is real and implemented

### Change-control rule

When architecture-affecting code changes land, update:

* this active spec when the target architecture changed;
* the frozen spec only for factual corrections or compatibility pointers;
* affected module docs in the same branch or change set.

---

## Configuration requirements

The active configuration must keep these parameters explicit:

* dataset identifier
* dataset root or dataset path
* output root
* flow key definition
* inactivity timeout
* sampling rate list
* sampling method
* size basis
* byte basis
* plotting mode
* cache policy
* worker count or parallelism limit
* logging mode and log level
* random seed when stochastic sampling is used

Do not bury these values in hard-coded constants without visibility.

---

## Parallelism and performance policy

### Priority rule

Correctness, methodology, reproducibility, and memory safety take priority over maximum throughput.

### Acceptable early parallelism

Safe early targets include:

* decompression across independent files;
* packet extraction across independent files;
* per-dataset execution after config resolution;
* per-rate work only after the shared `1:1` baseline is frozen;
* plotting from already computed metric tables.

### Deferred or restricted parallelism

Do not prioritise:

* independently rebuilding the same baseline in parallel;
* fine-grained parallelism inside stateful flow construction before the reference path is trusted;
* duplicated large packet tables per worker without explicit memory accounting.

### GPU policy

GPU support remains optional.
The active architecture must remain runnable and correct in CPU-only mode.

---

## Reproducibility requirements

Each run should record enough information to reproduce outputs, including:

* dataset identifier
* discovered source file names
* capture format
* flow key
* inactivity timeout
* sampling method
* sampling rate list
* size basis
* byte basis
* cache policy
* plotting mode
* software version or commit identifier when practical
* random seed when used

---

## Testing requirements

At minimum, include tests for:

* dataset-folder discovery
* resolved dataset config validation
* timeout-based flow splitting
* single-packet flows
* deterministic reconstruction on a tiny known example
* header-based capture-format detection for mislabeled but valid captures
* sampled-vs-baseline matching logic
* detection denominator correctness
* undefined handling for zero-duration cases
* one tiny end-to-end dataset-scoped run
* output-path determinism under `results/<dataset_id>/...`

---

## Definition of done for the active architecture

This active architecture is ready to freeze as `pipeline-v2.md` when all of the following are true:

1. the repository exposes one clear local entrypoint;
2. datasets are discovered as dataset-scoped folders under the input root;
3. per-dataset resolved configs are generated without mutating the shared template;
4. outputs are written under `results/<dataset_id>/meta`, `tables`, `plots`, and `logs`;
5. the core methodology remains unchanged from the frozen baseline;
6. persistent storage is simplified without losing reproducibility;
7. logging and manifests make runs inspectable;
8. tests cover the new execution model and key edge cases;
9. module documentation matches implemented behaviour.

---

## Non-goals

The following remain intentionally deferred:

* production deployment
* Kubernetes integration
* broad automated benchmarking
* exhaustive report generation
* GPU-dependent architecture
* large always-on intermediate storage trees
* multiple concurrent architecture specs for the same active code path

