---
name: local-pipeline-dev
description: Implement, debug, or refactor one stage of the local-first PCAP or PCAPNG analysis pipeline in this repository. Use when Codex needs to work on ingest, decompression, packet extraction, flow construction, sampling emulation, metric computation, plotting, or stage orchestration while preserving ground-truth-first methodology and validating each step before moving on.
---

# Local Pipeline Development

## Overview

Use this skill for code changes in the repository's analysis pipeline.

The priority is:
1. local correctness
2. methodological correctness
3. reproducibility
4. incremental performance improvements

Do not jump straight to Docker, Kubernetes, or cluster-specific work unless the user explicitly asks for it.

## Working Mode

Treat pipeline work as an iterative sequence, not a one-shot rewrite.

Preferred loop:
1. inspect the relevant files and current stage boundaries;
2. identify one stage, one bug, or one interface to change;
3. implement the smallest correct change;
4. validate immediately with focused tests or a small local run;
5. summarize what changed, what passed, and what remains;
6. only then move to the next stage.

When the task is large enough and multi-agent mode is enabled, a good split is:
- implementation agent
- validation agent
- optional monitor agent for long-running commands

Before spawning any worker, freeze the stage contract:
- the exact stage boundary;
- the dataset or fixture being used;
- the flow key;
- the inactivity timeout;
- the unit basis;
- the expected output or validation artefact.

Do not let separate workers invent their own stage contract or metric semantics.

## Default Stage Model

Unless the repository already defines a different structure, map work onto these stages:

1. dataset registry and validation
2. ingest and decompression
3. packet metadata extraction
4. ground-truth flow construction
5. sampling emulation or sampled-trace reconstruction
6. metric computation
7. plotting and report outputs

## Core Development Rules

- Preserve raw inputs as immutable.
- Prefer Parquet over large raw CSV files for intermediate artefacts.
- Use the `1:1` full-trace case as ground truth.
- Keep the inactivity timeout at `15 seconds` unless the user explicitly overrides it.
- Keep the flow key stable across baseline and sampled runs unless the user explicitly asks for a comparison.
- Add targeted tests whenever logic or metric definitions change.
- Make incremental changes where possible instead of rewriting the whole repository.

## Parallelism and Performance

Use performance work only after the reference logic is correct.

### CPU reference path
Every substantial stage should have a correct CPU path first.

### Parallelism rule
Prefer parallelism across:
- input files
- independent datasets
- clearly isolated chunks

Avoid fine-grained parallelism inside stateful flow construction until the simpler path is correct.

### GPU rule
Treat GPU acceleration as optional and isolated behind a backend or engine boundary.
GPU work is most appropriate for structured tabular operations such as joins, aggregations, and histogram pre-aggregation after packet data is already extracted.

Do not force GPU use into:
- decompression
- packet parsing
- correctness-critical flow-state logic

## Validation Expectations

After each meaningful code change, do at least one of the following:

- run focused unit tests;
- run a tiny local end-to-end example;
- compare new outputs against a known baseline on a small fixture;
- verify that metric definitions still match the documented formulas.

If validation cannot be completed, say exactly what blocked it.

## Expected Outputs

For each task, produce:

- the files changed;
- the specific stage affected;
- the validation performed;
- unresolved risks or edge cases;
- the next recommended step.

## Common Failure Cases

Avoid these mistakes:

- attempting to build the full pipeline in one pass;
- introducing performance optimisations before there is a trusted reference path;
- letting GPU and CPU backends produce different semantics;
- converting packet-scale intermediates into large raw CSV files by default;
- changing timeout, flow key, or units without surfacing the change;
- adding deployment work when the user only asked for local development.
