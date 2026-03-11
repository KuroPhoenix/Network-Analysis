# AGENTS.md

## Purpose

This repository supports the empirical evaluation of high-precision P4-based flow monitoring.

The goal of work in this repo is **not** to design the P4 monitoring system itself.
The goal is to use real full-trace network packet captures to show why full-flow monitoring matters by quantifying how packet sampling affects the completeness and accuracy of reconstructed flow records.

Unless the user explicitly overrides it, treat this repo as a **network trace analysis and evaluation** project, not a general software project.

---

## Project context

A broader team is working on a P4-based architecture that aims to capture complete flow records across multiple switches or routers with a single P4 switch.

Work in this repo should support that broader research goal by:

- collecting suitable full-trace datasets from external sources;
- reconstructing flow records from full traces;
- reconstructing flow records under different packet sampling rates;
- comparing sampled flow records against full-trace ground truth;
- producing clear analysis outputs that demonstrate why sampling can miss flows and distort flow statistics.

---

## Authority and document layout

Unless the user explicitly overrides it:

- `AGENTS.md` defines repo-wide operating rules, methodology constraints, execution priorities, and default working style.
- `docs/frozen/pipeline-mvp.md` is the frozen validated baseline architecture.
- `docs/hot/pipeline-v2.md` is the current evolution plan for post-MVP work.
- `docs/hot/git-workflow.md` defines branch, commit, checkpoint, and merge guidance.

If these documents appear to conflict, do not silently pick one interpretation.
Surface the conflict explicitly and reconcile it before proceeding.

Do **not** create extra policy trees or per-module documentation hierarchies unless the user explicitly asks for them.

---

## Current development priorities

Optimise in this order unless the user explicitly changes the order:

1. local correctness
2. methodological clarity
3. reproducibility
4. memory safety and space complexity
5. pipeline simplification
6. execution observability and logging
7. full plotting support
8. controlled partial parallelism
9. containerisation / deployment only when explicitly requested

Do not rush into Docker, Kubernetes, or cluster-specific changes while the local pipeline is still being refined.

---

## Post-MVP development stance

This repo is now beyond the MVP proof stage.

That does **not** mean the methodology is negotiable.
It means the implementation may evolve while the analysis contract stays stable.

Allowed post-MVP work includes:

- reducing peak memory use;
- reducing repeated full-table materialisation;
- simplifying module boundaries;
- improving orchestration and logging;
- enabling fuller plotting;
- introducing safe partial parallelism;
- tightening Git workflow and validation discipline.

Do not use post-MVP work as an excuse to silently redefine the baseline, metrics, timeout, or dataset standards.

---

## Working style for Codex

### Iterative development rule

For substantial tasks, work **stage by stage** instead of attempting a monolithic rewrite.

Preferred loop:

1. inspect existing code and relevant files;
2. isolate one stage, one bottleneck, one interface, or one bug;
3. implement the smallest correct change;
4. run targeted validation immediately;
5. report what passed, what failed, and what remains;
6. only then advance to the next safe step.

For multi-step pipeline work, prefer:

- one stage per task;
- one validation gate per stage;
- explicit notes about the next safe step.

Do **not** jump straight from an idea to a full end-to-end rewrite unless the user explicitly asks for that.

### Local-first execution rule

The local machine is the primary development target until correctness is established.

Assume:

- local execution comes before central scheduling;
- CPU reference implementations come before aggressive optimisation;
- GPU acceleration is optional and must not change result semantics.

### Non-interactive rule

Prefer deterministic, non-interactive commands with explicit input and output paths.

Avoid commands that block on prompts unless the user explicitly wants that behaviour.

---

## Resource-aware execution rules

Assume the default development target is a resource-constrained local machine in the rough range of:

- `32 GB RAM`
- `8 GB VRAM`

Treat RAM as the primary constraint for packet-scale processing.

Therefore:

- prefer streaming, chunked, or incremental processing over repeated full in-memory materialisation;
- avoid keeping multiple large packet-level tables resident unless clearly justified;
- avoid repeated full rereads when a smaller derived artefact would suffice;
- treat packet-level intermediates as optional debug artefacts when possible;
- prefer serial baseline construction before parallel work;
- parallelise only clearly isolated work units after the shared methodology contract is frozen.

Do not introduce a design that is elegant on paper but likely to exhaust local memory on realistic traces.

---

## Multi-agent guidance

Use sub-agents only when partitioning is clean and the coordination cost is justified.

When multi-agent mode is enabled, the **main agent owns the methodology contract**.

Worker agents may execute delegated steps, but they must not redefine:

- the flow key;
- the inactivity timeout;
- the `1:1` baseline definition;
- metric formulas or unit conventions;
- dataset acceptance thresholds or reporting rules.

Before spawning any worker agent for trace-analysis work, freeze and hand off the same minimum bundle to every worker:

- dataset identifier;
- baseline source and provenance;
- requested sampling rate or rates;
- flow key;
- inactivity timeout;
- unit basis;
- expected output schema.

Good cases for sub-agents:

- one agent for implementation and one for validation;
- one agent per dataset when comparing several datasets;
- one agent per `1:X` sampling rate only after the shared `1:1` baseline is fixed;
- one agent per metric family for broad result audits;
- one agent for code changes and one agent for result write-up;
- one agent for monitoring long-running local commands or repeated status checks.

Do not spawn sub-agents for:

- small single-file edits;
- trivial refactors;
- short debugging tasks where overhead exceeds useful work;
- independent attempts to redefine baseline construction or metric semantics.

Do not run **parallel methodology**.

In particular:

- do not let multiple agents independently reconstruct the `1:1` baseline and then choose between them;
- do not let separate agents reinterpret metric definitions or acceptance criteria;
- do not let sampled-trace workers compare against different baselines, timeouts, or unit bases.

When many agents are used, return a consolidated summary that clearly separates:

- completed work;
- validation findings;
- remaining risks or uncertainties;
- the next recommended step.

---

## Long-running iterative execution rule

For multi-stage implementation work, prefer repository-based progress tracking over repeated chat summaries.

Routine implementation history should default to Git branches, commits, and merge or pull-request descriptions rather than manual per-module changelogs.

Manual documentation updates are required when a change affects:

- current architecture or execution model;
- methodology or metric semantics;
- config schema or exposed parameters;
- output layout or result contracts;
- maintenance guidance that future work depends on.

Keep module `CHANGELOG.md` files in the repo, but use them only for purpose-, architecture-, direction-, or milestone-driven notes rather than routine implementation churn.

For each completed and validated stage:

- commit the changes;
- push them when task context and repository permissions allow;
- update the relevant document under `docs/hot/` when behaviour, priorities, or workflow guidance changed.

Use Git history together with the hot documents as the primary progress record for long-running work.

---

## Ground-truth-first evaluation rule

For any trace-analysis task, always follow a **ground-truth-first** methodology:

1. process the **unsampled full trace first**;
2. reconstruct the complete set of flow records from the unsampled trace;
3. treat those `1:1` flow records as the **ground-truth baseline**;
4. only after that, apply `1:X` sampling analysis;
5. compare every sampled result directly against the corresponding full-trace baseline.

Do **not** analyse sampled results in isolation.

Do **not** treat a sampled trace as acceptable ground truth.

Build the `1:1` baseline once and treat it as the shared reference for any later parallel sampling work.

---

## Canonical pipeline model

Unless the user explicitly requests a different workflow, treat the pipeline as:

1. dataset registry and validation
2. ingest / decompress / preserve raw inputs
3. packet-level metadata extraction
4. ground-truth flow construction
5. sampling emulation or sampled-trace reconstruction
6. metric computation
7. graphs and report outputs
8. deployment only when explicitly requested

Preferred conceptual flow:

`raw capture -> packet metadata -> baseline flows -> sampled flows -> comparisons -> plots`

Do not treat raw CSV as the main internal representation unless the user explicitly requires CSV.

---

## Data representation guidance

### Raw data handling

- Keep downloaded raw traces immutable.
- Preserve original archives and packet traces in a raw-data area.
- Do not overwrite raw captures during decompression or preprocessing.

### Intermediate format guidance

Prefer a compact structured format such as **Parquet** for packet-level and flow-level intermediate artefacts.

Avoid using large raw CSV files as the primary internal format when a columnar format is practical.

CSV is acceptable for:

- final summaries;
- small exports;
- interoperability outputs explicitly requested by the user.

### Suggested repository layout

Prefer a structure such as:

- `data/raw/` for untouched raw datasets
- `data/staged/` for decompressed inputs
- `data/processed/` for packet and flow intermediates
- `results/` for summaries, tables, and plots
- `logs/` for execution logs and run metadata
- `scripts/` for runnable entry points
- `src/` for reusable parsing, flow, sampling, metric, plotting, runtime, and logging code

---

## Flow definition

### Flow continuity rule

Use a fixed **15-second inactivity timeout** unless the user explicitly overrides it.

Interpretation:

- if packets belonging to the same flow are separated by **15 seconds or less**, they remain part of the same flow;
- if the gap exceeds **15 seconds**, the current flow record ends and a new flow record begins.

Do not silently change this timeout.

Do not compare experiments using different timeout values unless the user explicitly requests that comparison.

### Flow key

If the user does not specify otherwise, assume a standard **directional 5-tuple** flow key:

- source IP
- destination IP
- source port
- destination port
- protocol

If code, dataset metadata, or the professor's reference methodology makes the exact flow key explicit, use that explicit definition and report it.

If the flow key is ambiguous, state the ambiguity instead of guessing.

---

## Core metrics

Always prioritise these flow-level metrics:

- **Flow size estimation**
- **Flow duration**
- **Flow sending rate**
- **Flow detection rate**

These metrics evaluate both:

- **completeness**: whether real flows are detected at all;
- **accuracy**: whether detected sampled flows still resemble the true flow records.

### `1:1` sample rate

Treat the `1:1` case as the full-trace baseline.

Definitions:

- **Flow size** = accumulate the packets captured in the flow.
- **Flow duration** = duration derived from the actual observed flow packets in the full trace.
- **Flow sending rate** = size / duration.
- **Flow detection rate** = 100%.

### `1:X` sample rate

Treat every `1:X` case as a sampled approximation that must be evaluated against the `1:1` baseline.

Definitions:

- **Flow size** = number of captured packets in a flow × sampling rate.
- **Flow duration** = duration derived from the sampled packets only.
- **Flow sending rate** = sampled flow size / sampled flow duration.
- **Flow detection rate** = number of flows detected under the sampling scheme / actual number of flows in the full-trace baseline.

A flow that exists in the full trace but has no sampled packets must be treated as an **undetected flow**.

Do not silently exclude such flows from completeness analysis.

---

## Derived metrics

Support these distortion metrics when relevant:

- **Flow size overestimation factor** = sampled flow size / actual flow size
- **Flow duration underestimation factor** = sampled flow duration / actual flow duration
- **Flow sending rate overestimation factor** = flow size overestimation factor / flow duration underestimation factor

Interpret the duration ratio carefully:

- values below `1` indicate underestimation;
- values near `1` indicate closer agreement.

Do not mix packet-count and byte-count interpretations without explicitly stating so.

If size is measured in packets, report packets.
If size is measured in bytes, report bytes.
If both are reported, keep them explicitly separated.

---

## Expected interpretation under sampling

Unless evidence from a specific dataset shows otherwise, the default interpretation framework in this repo is:

- some real flows may not be detected at all under lower sampling rates;
- sampled flow records may still be inaccurate even when the flow is detected;
- flow size may be overestimated under the current sampled-size definition;
- flow duration may be underestimated because sampled packets may miss the true beginning or end of the actual flow;
- flow sending rate may therefore be overestimated because the numerator is inflated and the denominator is shortened.

State these as expected trends, not universal laws.

Still compute and report the actual measured results from the trace.

---

## Dataset acceptance rules

When collecting or recommending datasets, apply the following rules.

### Required dataset properties

1. The dataset should be **full-trace** packet capture data.
2. The dataset must **not** already be a sampled trace dataset.
3. The dataset should be from **2020 or later**.
4. Datasets from **2024–2026** are preferred when available.
5. The dataset should have **accurate timestamps**.
6. The dataset should preferably provide **lossless packet capture** where documented.
7. The dataset should preferably provide **full wire-format packet data** where documented.

### Diversity preference

Prefer datasets from diverse operational environments, such as:

- campus networks;
- backbone or national link networks;
- data centre networks;
- other real operational environments.

### Reporting rule for datasets

Whenever presenting a dataset candidate, explicitly state:

- source name;
- capture year;
- network domain;
- file format;
- whether it appears to be full-trace or sampled;
- whether the documented metadata supports accurate timestamps, losslessness, and full packet data;
- any uncertainty or caveats.

Do not present a weak or non-compliant dataset as if it fully satisfies the project requirements.

---

## Analysis workflow

For any trace-analysis task, follow this order unless the user explicitly requests otherwise.

1. **Inspect the input**
   - identify whether the input is PCAP, PCAPNG, compressed archive, CSV, Parquet, or metadata;
   - identify whether the dataset appears to be full-trace or sampled;
   - check for obvious truncation, missing metadata, or timestamp limitations.

2. **Establish the baseline**
   - reconstruct flows from the unsampled trace first;
   - use the 15-second inactivity rule;
   - record the baseline metrics.

3. **Apply sampling conditions**
   - run the requested `1:X` sampling rates;
   - keep the same flow definition and timeout.

4. **Compute comparisons**
   - flow size estimation
   - flow duration
   - flow sending rate
   - flow detection rate
   - flow size overestimation factor
   - flow duration underestimation factor
   - flow sending rate overestimation factor

5. **Report against ground truth**
   - make the `1:1` baseline explicit;
   - compare each sampling case directly against that baseline;
   - distinguish between undetected flows and inaccurate detected flows.

---

## Performance guidance

### CPU first, then optional GPU

Default to a correct CPU implementation first.

Only add GPU-backed execution after the CPU path is correct and validated.

Do not assume GPU acceleration is appropriate for every stage.

### Likely CPU-oriented stages

These are usually I/O-bound, parser-bound, or stateful enough that CPU-first is the safer default:

- decompression
- packet parsing
- packet metadata extraction
- flow construction
- boundary reconciliation across chunks

### Likely GPU-suitable stages

These are the best candidates for optional GPU acceleration once data is already in structured tabular form:

- dataframe aggregations
- joins between baseline and sampled flow tables
- histogram or CDF pre-aggregation
- large metric summarisation
- optional plotting pre-aggregation

### Parallelism rule

Parallelise **across files** or clearly isolated work units before attempting fine-grained parallelism inside one ordered flow-construction task.

Safe first targets:

- decompression across files;
- packet extraction across independent files;
- per-rate work only after the shared `1:1` baseline is frozen;
- plotting from already computed metric tables.

Unsafe targets until explicitly justified:

- independently rebuilding the baseline in parallel;
- changing flow-boundary semantics for throughput;
- duplicating large packet-scale tables per worker without memory accounting.

If traces are chunked in time, preserve enough overlap to avoid breaking flows at chunk boundaries.

The overlap must respect the active inactivity timeout.

### Determinism rule

When randomness is used, such as random packet sampling:

- expose the random seed;
- record the sampling rule;
- keep outputs reproducible.

---

## Logging and execution observability

Execution should become easier to monitor over time, but observability must stay simple and reproducible.

When adding or refactoring logging:

- prefer one clear run identifier per invocation;
- keep logs separate from analysis artefacts;
- log stage start, stage end, input identifiers, output paths, and failure summaries;
- avoid noisy logging that hides methodological events;
- prefer deterministic log filenames and stable log locations.

If a logging framework is introduced, it must not make local execution harder to understand or debug.

---

## Coding expectations

### General

- Prefer **Python** unless the user explicitly requests another language.
- Write modular code with small functions and explicit parameters.
- Use clear function names and basic docstrings for public functions.
- Use type hints when practical.
- Fail loudly on malformed input rather than silently producing questionable output.

### Parameter visibility

Do not hide important assumptions in hard-coded constants.

At minimum, make these visible and easy to find:

- sampling rate(s)
- inactivity timeout
- flow key definition
- whether size means packets or bytes
- dataset name
- random seed when randomness is used
- execution backend when CPU/GPU choice exists

### Validation expectations

When code changes methodology, metric logic, orchestration, logging, or performance-sensitive behaviour:

- add or update focused tests;
- validate with at least one small local example when practical;
- report unresolved edge cases explicitly;
- state whether the change was semantic, structural, or operational only.

### File naming

Prefer descriptive output names that include:

- dataset name
- timeout
- sampling rate
- metric type
- unit basis where relevant

Example:

`{dataset}_{timeout}s_{samplerate}x_packets_metrics.csv`

---

## Reporting expectations

When generating summaries, tables, or discussion text:

- always identify the dataset being discussed;
- always state that the `1:1` case is the ground-truth baseline;
- always state the sampling rate being discussed;
- always state whether flow size refers to packets or bytes;
- explicitly distinguish between completeness loss and metric distortion;
- explicitly mention caveats or missing dataset metadata.

Do not write vague claims such as “sampling affected the results”.

Be specific about:

- which metric changed;
- in what direction it changed;
- whether flows were missed entirely or merely mismeasured.

---

## Git and repository hygiene

This repo should normally track:

- code
- documentation
- processed summaries
- figures
- small result files
- small reproducible test fixtures

This repo should normally **not** track:

- large raw packet captures
- large dataset archives
- temporary extraction directories
- IDE files
- virtual environments
- large generated intermediates that can be reproduced locally

Respect `.gitignore` and keep raw trace files out of normal Git history unless the user explicitly asks otherwise.

For substantial work:

- checkpoint before large edits;
- commit after each validated slice;
- keep architecture-affecting code and doc updates in the same branch;
- prefer small, reviewable commits over one large opaque commit.

---

## Default behaviour for Codex

Unless the user explicitly overrides these rules, Codex should:

- treat this repo as a flow-analysis evaluation project;
- use full-trace ground truth first;
- keep the inactivity timeout at 15 seconds;
- compare all `1:X` cases against the `1:1` baseline;
- prioritise correctness, methodological clarity, reproducibility, and memory safety over speed;
- preserve the repo’s existing direction and make incremental changes where possible;
- work iteratively with explicit validation gates;
- prefer local-first development over premature deployment work;
- update `docs/hot/` when post-MVP implementation behaviour or workflow guidance changes.

---

## Review guidelines

Treat the following as review-worthy issues even when the code still runs:

- any silent change to the 15-second timeout;
- any code or prose that mixes packet-based and byte-based flow size without explicit labelling;
- any workflow that uses sampled traces as ground truth;
- any analysis that reports sampled metrics without comparing them to the `1:1` baseline;
- any logic that silently drops undetected flows from the denominator for flow detection;
- any inconsistency between documented metric definitions and implemented formulas;
- any optimisation that changes metric semantics or removes the CPU reference path;
- any commit that accidentally includes raw datasets, archives, or large capture files that should be ignored;
- any performance change that increases peak memory use without justification;
- any parallelism change that weakens baseline consistency or reproducibility.

Prioritise correctness of methodology, metric definitions, units, reproducibility, memory safety, and validation over formatting issues.

For this repository, methodology errors in analysis code or reporting are often more important than ordinary stylistic defects.

---

## Long-running task guidance

- Prefer non-interactive commands.
- Prefer commands with clear output, explicit paths, and deterministic filenames.
- When a task is expected to take time, state what is being run, what output is expected, and what completion condition is being checked.
- Use monitor or wait-style behaviour for repeated polling or status checks when available.
