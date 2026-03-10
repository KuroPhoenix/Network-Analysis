# AGENTS.md

## Purpose

This repository supports the empirical evaluation of high-precision P4-based flow monitoring.

The goal of work in this repo is **not** to design the P4 monitoring system itself. The goal is to use real full-trace network packet captures to show why full-flow monitoring matters by quantifying how packet sampling affects the completeness and accuracy of reconstructed flow records.

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

## Current development priority

Optimise first for:
1. **local correctness**
2. **methodological clarity**
3. **reproducibility**
4. **incremental performance improvements**
5. **containerisation and Kubernetes integration only when explicitly requested**

Do not rush into Docker, Kubernetes, or cluster-specific changes while the local pipeline is still being validated.

---

## Document hierarchy and authority

Unless the user explicitly overrides it:

- `AGENTS.md` defines repo-wide operating rules, methodology constraints, and default working style.
- `docs/specs/pipeline-mvp.md` defines the MVP architecture, module responsibilities, and implementation contracts. `docs/pipeline-mvp.md` may remain as a compatibility pointer, but the canonical spec path is under `docs/specs/`.
- `docs/modules/<module-name>/` contains module-local explanations, maintenance notes, and change history. If such file or directory does not exist, that indicates this module has not yet been implemented. Therefore, create the necessary folders and markdown files before writing the docs.

If these documents appear to conflict, do not silently choose one interpretation. Surface the conflict explicitly and reconcile it before proceeding.

## Working style for Codex

### Iterative development rule
For substantial tasks, work **stage by stage** instead of attempting a monolithic rewrite.

Preferred loop:
1. inspect existing code and relevant files;
2. isolate one stage or one bug;
3. implement the smallest correct change;
4. run targeted validation immediately;
5. report what passed, what failed, and what remains;
6. only then advance to the next stage.

For multi-step pipeline work, prefer:
- one stage per task;
- one validation gate per stage;
- explicit notes about the next safe step.

Do **not** jump straight from an idea to a full end-to-end rewrite unless the user explicitly asks for that.

### Local-first execution rule
The local machine is the primary development target until correctness is established.

Assume:
- local execution comes before central Kubernetes scheduling;
- CPU reference implementations come before aggressive optimisation;
- GPU acceleration is optional and should not change the semantics of the results.

### Non-interactive rule
Prefer deterministic, non-interactive commands with explicit input and output paths.
Avoid commands that block on prompts unless the user explicitly wants that behaviour.

---

## Multi-agent guidance

Use sub-agents only when partitioning is clean and the coordination cost is justified.

When multi-agent mode is enabled, the **main agent owns the methodology contract**. Worker agents may execute delegated steps, but they must not redefine:
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
- one agent for code changes and one agent for result writeup;
- one agent for monitoring long-running local commands or repeated status checks.

Do not spawn sub-agents for:
- small single-file edits;
- trivial refactors;
- short debugging tasks where overhead exceeds useful work.
- independent attempts to redefine baseline construction or metric semantics.

When multi-agent mode is enabled and a task is large enough, prefer this pattern:
1. main agent defines the scope;
2. main agent freezes the methodology contract and handoff bundle;
3. implementation agent changes code or executes one clean analysis slice;
4. validation agent checks logic, tests, and metric definitions against the frozen contract;
5. main agent consolidates findings and either advances or stops at the validation gate.

Do not run **parallel methodology**. In particular:
- do not let multiple agents independently reconstruct the `1:1` baseline and then choose between them;
- do not let separate agents reinterpret metric definitions or acceptance criteria;
- do not let sampled-trace workers compare against different baselines, timeouts, or unit bases.

When many agents are used, return a consolidated summary that clearly separates:
- completed work;
- validation findings;
- remaining risks or uncertainties;
- the next recommended step.

## Long-running iterative execution rule

For multi-stage implementation work, prefer repository-based progress tracking over repeated chat summaries.

For each completed and validated module or stage:
- commit the changes;
- push them when task context and repository permissions allow;
- update the corresponding documentation under `docs/modules/<module-name>/`.

Use Git history together with module documentation as the primary progress record for long-running work.

---

## Ground-truth-first evaluation rule

For any trace-analysis task, always follow a **ground-truth-first** methodology:

1. Process the **unsampled full trace first**.
2. Reconstruct the complete set of flow records from the unsampled trace.
3. Treat those `1:1` flow records as the **ground truth baseline**.
4. Only after that, apply `1:X` sampling analysis.
5. Compare every sampled result directly against the corresponding full-trace baseline.

Do **not** analyse sampled results in isolation.
Do **not** treat a sampled trace as acceptable ground truth.
Build the `1:1` baseline once and treat it as the shared reference for any later parallel sampling work.

---

## Canonical pipeline model

Unless the user explicitly requests a different workflow, treat the pipeline as:

1. **Dataset registry and validation**
2. **Ingest / decompress / preserve raw inputs**
3. **Packet-level metadata extraction**
4. **Ground-truth flow construction**
5. **Sampling emulation or sampled-trace reconstruction**
6. **Metric computation**
7. **Graphs and report outputs**
8. **Containerisation / deployment** only when explicitly requested

This means the preferred conceptual flow is:

`raw capture -> packet metadata -> baseline flows -> sampled flows -> comparisons -> plots`

Do not treat `raw CSV` as the main internal representation unless the user explicitly requires CSV.

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

### Suggested directory structure
Prefer a structure such as:
- `data/raw/` for untouched raw datasets
- `data/staged/` for decompressed inputs
- `data/processed/` for packet and flow intermediates
- `results/` for summaries, tables, and plots
- `scripts/` for runnable entry points
- `src/` for reusable parsing, flow, sampling, metric, and plotting code

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
   - Identify whether the input is PCAP, PCAPNG, compressed archive, CSV, Parquet, or metadata.
   - Identify whether the dataset appears to be full-trace or sampled.
   - Check for obvious truncation, missing metadata, or timestamp limitations.

2. **Establish the baseline**
   - Reconstruct flows from the unsampled trace first.
   - Use the 15-second inactivity rule.
   - Record the baseline metrics.

3. **Apply sampling conditions**
   - Run the requested `1:X` sampling rates.
   - Keep the same flow definition and timeout.

4. **Compute comparisons**
   - Flow size estimation
   - Flow duration
   - Flow sending rate
   - Flow detection rate
   - Flow size overestimation factor
   - Flow duration underestimation factor
   - Flow sending rate overestimation factor

5. **Report against ground truth**
   - Make the `1:1` baseline explicit.
   - Compare each sampling case directly against that baseline.
   - Distinguish between undetected flows and inaccurate detected flows.

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

### Parallelism rule
Parallelise **across files** or clearly isolated chunks before attempting fine-grained parallelism inside one ordered flow-construction task.

If traces are chunked in time, preserve enough overlap to avoid breaking flows at chunk boundaries. The overlap must respect the active inactivity timeout.

### Determinism rule
When randomness is used, such as random packet sampling:
- expose the random seed;
- record the sampling rule;
- keep outputs reproducible.

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
When code changes methodology or metric logic:
- add or update focused tests;
- validate with at least one small local example when practical;
- report any unresolved edge cases explicitly.

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

## Module Documentation and Change Tracking

For each pipeline module, create a dedicated folder under `docs/modules/<module-name>/` containing explanatory documentation that helps both users and future Codex agents understand, use, and maintain the module correctly.

Each module folder should contain at least the following files:

### `README.md`
This file explains the module in depth. It should include:
- the purpose of the module;
- its inputs and outputs, including expected formats and schemas where relevant;
- the methodology and implementation logic used by the module;
- assumptions, constraints, and known limitations;
- its dependencies on upstream modules and the contract it provides to downstream modules.

### `CHANGELOG.md`
This file records meaningful modifications to the module over time. Each entry should include:
1. the purpose of the modification;
2. what changed;
3. the impact on other modules or pipeline stages;
4. any required maintenance or follow-up updates.

### `Maintenance.md`
This file should contain:
- usage notes;
- maintenance guidelines;
- operational caveats;
- recommendations for future extension, refactoring, or debugging.

Whenever a modification changes the module’s behaviour, interface, assumptions, or integration with other stages, update `README.md`, `CHANGELOG.md`, and `Maintenance.md` accordingly.

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



## What to avoid

Do not:
- treat sampled public trace datasets as acceptable substitutes for full-trace ground truth;
- silently change the flow timeout;
- mix packets and bytes without stating the unit;
- ignore undetected flows when reporting flow detection effects;
- overclaim from a single dataset or a single sampling rate;
- rewrite the whole codebase when an incremental change is enough;
- commit large raw datasets or trace archives into Git;
- force GPU usage into stages where it changes correctness assumptions;
- replace a validated CPU reference path with an unvalidated accelerated path.

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
- large archives of datasets
- temporary extraction directories
- IDE files
- virtual environments
- large generated intermediates that can be reproduced locally

Respect `.gitignore` and keep raw trace files out of normal Git history unless the user explicitly asks otherwise.

---

## Default behaviour for Codex

Unless the user explicitly overrides these rules, Codex should:
- treat this repo as a flow-analysis evaluation project;
- use full-trace ground truth first;
- keep the inactivity timeout at 15 seconds;
- compare all `1:X` cases against the `1:1` baseline;
- prioritise correctness, methodological clarity, and reproducibility over speed;
- preserve the user's existing repo structure and make incremental changes where possible;
- work iteratively with explicit validation gates;
- prefer local-first development over premature deployment work.

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
- any commit that accidentally includes raw datasets, archives, or large capture files that should be ignored.

Prioritise correctness of methodology, metric definitions, units, reproducibility, and validation over formatting issues.

For this repository, methodology errors in analysis code or reporting are often more important than ordinary stylistic defects.

---

## Long-running task guidance

- Prefer non-interactive commands.
- Prefer commands with clear output, explicit paths, and deterministic filenames.
- When a task is expected to take time, state what is being run, what output is expected, and what completion condition is being checked.
- Use monitor or wait-style behaviour for repeated polling or status checks when available.
