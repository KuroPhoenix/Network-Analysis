# Pipeline MVP Specification

## Purpose

This document defines the minimum viable implementation for the local-first packet-trace analysis pipeline in this repository.

The goal of the MVP is **not** to build the lab's full production deployment or the underlying P4 monitoring system. The goal is to produce a **runnable, modular, reproducible local pipeline** that:

1. ingests real packet-capture datasets;
2. reconstructs unsampled ground-truth flows;
3. reconstructs sampled flows under one or more `1:X` packet-sampling conditions;
4. measures how sampling affects flow detection and flow-level metrics; and
5. emits inspectable outputs and at least one minimal analysis graph.

This MVP should be suitable for later containerisation and submission to the lab's central Kubernetes environment, but Kubernetes integration is explicitly **out of scope** for the MVP itself.

---

## Design principles

### 1. Ground-truth first
Always process the unsampled full trace first. The `1:1` case is the ground-truth baseline. Every sampled `1:X` result must be compared directly against that baseline.

### 2. Modular pipeline modules
Each pipeline module must be implemented as a separate module with a clear input contract, output contract, and validation boundary.

### 3. Thin orchestration
The final runnable entrypoint should be a **thin driver** that composes the pipeline modules. It must not hide methodology decisions or contain the core business logic.

### 4. Local correctness before scale
The MVP must work correctly and reproducibly on a single machine before optimisation, Docker packaging, or Kubernetes scheduling are attempted.

### 5. CPU reference path first
The default implementation path must be CPU-based and deterministic. GPU acceleration is optional and should only be introduced later for dataframe-heavy aggregation work where it materially helps.

### 6. Inspectable intermediate artefacts
Intermediate results should be preserved in compact, structured formats so that errors can be traced module by module.

### 7. Parquet over CSV
Do not use raw CSV as the primary intermediate format for packet-scale data. Prefer Parquet for packet tables, flow tables, metric tables, and other structured intermediate outputs.

### 8. Explicit methodology
Important assumptions must be visible in configuration and documentation, not buried in code. This includes timeout, flow key, sampling rates, size basis, and dataset identity.

### 9. Lightweight runtime visibility
The local MVP should expose lightweight runtime feedback for long-running local runs. Progress bars and elapsed-time logging are encouraged when they remain optional, deterministic, and separate from the metric logic.

### 10. Module documentation requirement

Module-level documentation and change-tracking requirements are defined in `AGENTS.md`.

For each implemented module, maintain documentation under:

`docs/modules/<module-name>/`

At minimum, each module should provide:
- `README.md`
- `CHANGELOG.md`
- `Maintenance.md`

These documents must be kept consistent with the implemented behaviour, interfaces, assumptions, and downstream/upstream integration of the module.



---

## Scope of the MVP

### Module naming note
`AGENTS.md` defines the canonical conceptual pipeline as:

1. dataset registry and validation
2. ingest and decompression
3. packet extraction to a canonical packet table
4. ground-truth flow construction
5. sampling emulation or sampled reconstruction
6. metric computation against baseline
7. plotting and report outputs
8. containerisation and deployment only when explicitly requested

This MVP specification describes the detailed implementation scope starting at ingest, but the codebase should still reserve a distinct `dataset_registry` module and should prefer **named pipeline modules** over numeric stage IDs in imports, file names, and documentation. This avoids ambiguity between the repo-wide conceptual pipeline and the narrower MVP implementation sequence.

The MVP must cover these modules:

1. **Ingest / decompress**
2. **Packet extraction to canonical packet table**
3. **Ground-truth flow construction**
4. **Sampling emulation or sampled packet ingestion**
5. **Metric computation against baseline**
6. **Thin driver for end-to-end local execution**
7. **At least one minimal plot or analysis output**

The MVP does **not** need to include:

- Docker image packaging;
- Kubernetes job specifications;
- distributed execution;
- large-scale benchmarking;
- production-grade optimisation;
- multiple plotting backends;
- advanced GPU-specific code paths.

---

## Accepted inputs

### Capture formats
The MVP must accept packet captures in **PCAP or PCAPNG** format.

When the raw or staged capture bytes are directly readable, capture-format detection should prefer the file header over the filename suffix. This avoids misclassifying valid captures whose extensions do not match their actual wire format.

### Compression
The ingest module may also accept compressed archives when practical, such as `.gz`, `.xz`, `.zip`, or `.rar`, provided the decompression path is explicit and the original raw file remains untouched.

### Dataset requirements
The intended research workflow assumes:

- **full-trace** packet capture data;
- **not** already sampled trace datasets as the source baseline;
- capture year preferably **2020 or later**;
- datasets from **2024–2026 preferred** when available;
- accurate per-packet timestamps;
- preferably documented **lossless capture**;
- preferably documented **full wire-format packet data**.

The MVP should preserve enough metadata to report uncertainty if these properties are only partially documented.

---

## Methodology specification

### Baseline rule
The `1:1` full-trace reconstruction is the only ground-truth baseline in the MVP.

### Sampling rule
Each `1:X` condition is evaluated as a sampled approximation. Every sampled result must be compared directly against the `1:1` baseline, not against another sampled rate.

### Flow continuity rule
Use a default inactivity timeout of **15 seconds** unless explicitly overridden in configuration.

Interpretation:
- packet gaps of **15 seconds or less** stay within the same flow record;
- packet gaps **greater than 15 seconds** terminate the current flow and start a new one.

### Flow key rule
The default flow key is the directional 5-tuple:
- source IP
- destination IP
- source port
- destination port
- protocol

If a dataset or task requires a different flow key, the override must be stated explicitly.

### Size basis rule
The pipeline must keep the size basis explicit:
- `packets`
- `bytes`
- or both, if both are computed deliberately and labelled clearly

Do not mix packet-based and byte-based metrics without explicit labels.

### Reporting rule for expected effects
The repo may expect some directional sampling effects, but the MVP must treat these as **expected trends**, not universal laws. The code and reports must compute and report measured outcomes from the data rather than forcing predetermined conclusions.

---

## Metric definitions

The MVP must support these flow-level metrics:

### Baseline metrics (`1:1`)
- **Flow Byte size** = total byte count observed in the full trace for the reconstructed flow 
- **Flow Packet size** = total packet count observed in the full trace for the reconstructed flow
- **Flow duration** = `last_packet_timestamp - first_packet_timestamp`
- **Flow byte sending rate** = `flow byte size / flow duration`
- **Flow byte sending rate** = `flow packet size / flow duration`
- **Flow detection rate** = `100%`


### Sampled metrics (`1:X`)
- **Sampled flow packet size estimate** = sampled packets observed in the reconstructed sampled flow × sampling rate, unless the experiment explicitly uses another estimator
- **Sampled flow byte size estimate** = total sampled bytes observed in the reconstructed sampled flow × sampling rate, unless the experiment explicitly uses another estimator. The accumulation formula is as follows:
```
For each packet's byte size:
    total size += packet byte size * sampling rate
```
- **Sampled flow duration** = `last_sampled_packet_timestamp - first_sampled_packet_timestamp` within the sampled reconstruction only
- **Sampled flow packet sending rate** = `sampled flow packet size estimate / sampled flow duration`
- **Sampled flow size sending rate** = `sampled flow byte size estimate / sampled flow duration`
- **Flow detection rate** = `detected baseline flows / total baseline flows`

### Derived distortion metrics
Use these definitions in the MVP:

- **Flow packet size overestimation factor** = `sampled flow size estimate / actual baseline flow size`
- **Flow byte size overestimation factor** = `sampled flow size estimate / actual baseline flow size`
- **Flow duration underestimation factor** = `sampled flow duration / actual baseline flow duration`
- **Flow byte sending rate overestimation factor** = `flow byte size overestimation factor / flow duration underestimation factor`
- **Flow packet sending rate overestimation factor** = `flow packet size overestimation factor / flow duration underestimation factor`

### Undefined cases
If a denominator is zero, the metric must be represented as explicitly undefined, such as `NA`, `null`, or another clearly documented non-numeric value.

This applies especially to:
- zero-duration flows;
- rates derived from zero-duration flows;
- ratio metrics whose denominator is zero.

For these null-flows, filter them out for the subsequent flow metric calculation and plotting.

---

## Module-by-module specification

## Module 1: Ingest / decompress

### Purpose
Discover raw input files, validate their basic format, and decompress them into a staged area without modifying the original raw artefacts.

### Inputs
- one or more raw files under a configured input directory;
- supported formats such as `.pcap`, `.pcapng`, `.pcap.gz`, `.pcapng.gz`, `.xz`, `.zip`, `.rar`, or other explicitly supported wrappers;
- dataset-level metadata if available.

### Outputs
- staged packet-capture files ready for parsing;
- a small manifest or metadata record describing:
  - source file;
  - staged file path;
  - detected format;
  - compression type if any;
  - checksum if available;
  - dataset identifier.

### Rules
- raw files must remain immutable;
- decompression must be explicit and reproducible;
- capture-format detection should prefer readable capture headers over filename suffixes when the bytes are available locally;
- failures must be surfaced clearly rather than silently skipped.

### Validation
- file discovery works for the configured input path;
- decompression produces readable staged files;
- header-based capture-format detection handles mislabeled but valid captures;
- manifest metadata is generated consistently.

---

## Module 2: Packet extraction

### Purpose
Convert each staged packet capture into a canonical packet table suitable for flow reconstruction.

### Inputs
- staged `PCAP` or `PCAPNG` files;
- packet parser configuration;
- optional dataset metadata.

### Required packet fields
The MVP packet table should include, at minimum:
- `dataset_id`
- `source_file`
- `packet_index`
- `packet_size` in bytes
- `timestamp` 
- `captured_len`
- `wire_len` if available
- `protocol`
- `src_ip`
- `dst_ip`
- `src_port`
- `dst_port`
- `tcp_flags` when applicable

Optional fields may be added if clearly documented.

### Outputs
- one canonical packet table per input trace, preferably as Parquet;
- optional packet extraction metadata such as packet count and field availability.

### Rules
- preserve packet order semantics;
- keep timestamp fidelity intact;
- fail loudly if essential fields for flow reconstruction cannot be derived.

### Validation
- schema matches the required packet table contract;
- a tiny sample capture can be extracted successfully;
- a mislabeled but valid capture still parses when header detection resolves the true format;
- output is readable by the flow-construction module.

---

## Module 3: Ground-truth flow construction

### Purpose
Reconstruct directional flow records from the unsampled packet table.

### Inputs
- canonical packet table;
- explicit or default flow key;
- inactivity timeout, defaulting to `15s`.

### Outputs
A baseline flow table with, at minimum:
- `dataset_id`
- `flow_id`
- flow-key fields
- `start_ts`
- `end_ts`
- `duration`
- `packet_count` and `byte_count`
- `sending_rate_packets` and `sending_rate_bytes`
- any labels needed to state the size basis clearly

### Rules
- use the directional 5-tuple by default unless overridden;
- use the configured inactivity timeout consistently;
- single-packet flows are valid flows;
- deterministic input should produce deterministic flow reconstruction.

### Validation
- test timeout splitting at the `15s` boundary;
- test timeout splitting when the gap is greater than `15s`;
- test single-packet flow handling;
- test deterministic reconstruction on a tiny known input.

---

## Module 4: Sampling emulation or sampled reconstruction

### Purpose
Produce sampled packet streams or sampled flow reconstructions under one or more `1:X` packet-sampling conditions.

### Inputs
- canonical packet table or baseline-compatible packet source;
- one or more sampling rates such as `1:10`, `1:100`, or another explicit list;
- one explicit sampling procedure.

### Outputs
- sampled packet tables and/or sampled flow tables;
- sampling metadata per run, including:
  - dataset identifier;
  - sampling rate;
  - sampling method;
  - random seed if stochastic sampling is used.

### Rules
- do not treat an externally supplied sampled trace as ground truth;
- if external sampled traces are accepted for comparison, their provenance relative to the full trace must be stated explicitly;
- sampled flows must be reconstructed from sampled packets only;
- do not scale full baseline flow records directly without reconstructing sampled observations.

### Validation
- `1:1` path behaves as the no-loss reference case;
- at least one `1:X` sampling path runs successfully;
- sampled outputs are consumable by the metrics module;
- provenance and sampling settings are recorded explicitly.

---

## Module 5: Metric computation

### Purpose
Match sampled flow records to baseline flows and compute flow detection and distortion metrics.

### Inputs
- baseline flow table;
- sampled flow table(s);
- flow key definition;
- timeout configuration;
- size basis.

### Outputs
At minimum:
- one summary table per sampled rate containing:
  - total baseline flow count
  - detected baseline flow count
  - undetected baseline flow count
  - flow detection rate
- one metric table containing:
  - baseline size in bytes
  - baseline size in packets
  - sampled size in bytes estimate
  - sampled size in packets estimate
  - baseline duration
  - sampled duration
  - baseline sending rate in bytes/sec
  - baseline sending rate in packets/sec
  - sampled sending rate in bytes/sec
  - sampled sending rate in packets/sec
  - flow packet size overestimation factor
  - flow byte size overestimation factor
  - flow duration underestimation factor
  - flow sending rate (byte) overestimation factor
  - flow sending rate (packet) overestimation factor
  - detection status

### Rules
- match every sampled result directly against the `1:1` baseline;
- keep undetected flows in the detection denominator;
- do not drop undetected flows silently when reporting detection effects;
- label every metric with its unit basis when relevant.

### Validation
- sampled-vs-baseline matching logic is tested;
- detection denominator uses total baseline flows;
- derived metrics follow the repo definition;
- zero-duration and undefined cases are handled explicitly.

---

## Module 6: Thin driver / orchestrator

### Purpose
Provide one runnable local command that composes the implemented modules into an end-to-end MVP.

### Inputs
- config file;
- input dataset path;
- output directory;
- selected sampling rates;
- optional module-selection flags if partial runs are supported.

### Outputs
- staged files;
- packet tables;
- baseline flow tables;
- sampled flow tables;
- metric tables;
- at least one minimal analysis output.

### Rules
- the driver must remain thin;
- module logic belongs in the pipeline modules, not the driver;
- configuration should drive methodology-relevant behaviour;
- runtime feedback such as progress bars and elapsed-time logging must not change pipeline semantics.

### Validation
- one tiny end-to-end local run completes successfully;
- outputs are written to predictable locations;
- per-module and per-dataset elapsed times are visible during runnable local executions;
- run instructions are documented.

---

## Module 7: Minimal plotting

### Purpose
Produce at least one minimal visual output that demonstrates the end-to-end pipeline is working.

### Recommended MVP plots
Choose one or more of:
- flow detection rate vs sampling rate;
- CDF or histogram of flow size overestimation factor;
- CDF or histogram of flow duration underestimation factor;
- CDF or histogram of flow sending rate overestimation factor.

### Inputs
- metric tables from Module 5.

### Outputs
- one or more static figure files;
- optional summary CSV/Parquet tables used to generate the figure.

### Rules
- plotting is secondary to correctness;
- keep the plotting module lightweight and reproducible;
- use clear labels, including unit basis where relevant.

### Validation
- at least one plot renders from the MVP example;
- plotted values correspond to generated metric outputs.

---

## Recommended repository layout

```text
project/
  configs/
    pipeline.yaml
    datasets.yaml
    sampling.yaml
  data/
    raw/
    staged/
    processed/
  docs/
    specs/
      pipeline-mvp.md
    modules/
  results/
    tables/
    plots/
  scripts/
  src/
    <package_name>/
      cli.py
      shared/
      modules/
        dataset_registry.py
        ingest.py
        packet_extraction.py
        flow_construction.py
        sampling.py
        metrics.py
        plotting.py
      pipeline/
        driver.py
  tests/
```

The exact layout may vary, but the MVP should preserve the distinction between:
- raw data;
- derived intermediate artefacts;
- results;
- reusable source code;
- tests;
- documentation.

---

## Configuration requirements

The MVP configuration must make these parameters explicit and easy to inspect:

- dataset name or identifier;
- input path(s);
- output path(s);
- flow key definition;
- inactivity timeout;
- sampling rate list;
- sampling method;
- size basis: both packets, bytes;
- plotting enable/disable or plot selection;
- worker count if CPU parallelism is exposed.

Do not bury these values in hard-coded constants without visibility.

---

## Parallelism and performance policy

### MVP rule
Correctness takes priority over maximum throughput.

### Acceptable early parallelism
The MVP may expose CPU parallelism for:
- decompression across files;
- packet extraction across files;
- later metric aggregation across independent sampled runs.

### Deferred optimisation
The MVP does not need to parallelise:
- complex chunk-boundary flow assembly across one giant capture;
- GPU-specific flow reconstruction;
- distributed execution.

### GPU policy
GPU support is optional and should be isolated behind a clear backend boundary if added later. The MVP must remain runnable in CPU-only mode.

---

## Reproducibility requirements

Each completed run should record enough information to reproduce the outputs, including:

- dataset identifier;
- source file name(s);
- capture format;
- flow key;
- inactivity timeout;
- sampling method;
- sampling rate(s);
- size basis;
- software version or commit identifier when practical;
- any random seed used for stochastic sampling.

---

## Testing requirements

The MVP must include tests for the logic it implements.

At minimum, include tests for:
- timeout-based flow splitting;
- single-packet flows;
- deterministic reconstruction on a tiny known example;
- header-based capture-format detection for mislabeled but valid captures;
- sampled-vs-baseline matching logic;
- detection denominator correctness;
- undefined handling for zero-duration cases;
- one tiny end-to-end run.

---

## Definition of done

The MVP is complete when all of the following are true:

1. the repository contains modular implementations of the core pipeline modules;
2. the repository contains a thin driver/orchestrator;
3. a small local example can run end to end;
4. baseline and sampled outputs are written in inspectable structured formats;
5. the key flow metrics and derived distortion metrics are computed consistently;
6. at least one minimal analysis plot is produced;
7. tests cover the implemented logic and key edge cases;
8. the methodology assumptions used by the code match this specification.

---

## Non-goals for the MVP

The following are intentionally deferred:

- full production deployment;
- lab Kubernetes integration;
- large-dataset optimisation;
- broad multi-dataset benchmarking;
- exhaustive UI/report generation;
- automatic paper-ready interpretation.

The MVP should solve the methodology and implementation foundation first.
