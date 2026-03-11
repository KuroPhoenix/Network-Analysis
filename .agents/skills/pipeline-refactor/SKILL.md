---
name: pipeline-refactor
description: Implement, debug, optimise, or refactor one stage of the local-first PCAP or PCAPNG analysis pipeline in this repository. Use when working on space or time complexity, memory safety, pipeline simplification, safe partial parallelism, plotting support, logging and observability, or stage orchestration while preserving ground-truth-first methodology, a frozen 1:1 baseline contract, and iterative validation after each slice.
---

# Pipeline Refactor

## Overview

Use this skill for code changes in the repository's analysis pipeline after the MVP stage.

The priority order is:

1. local correctness
2. methodological correctness
3. reproducibility
4. memory safety
5. pipeline simplification
6. observability and logging
7. full plotting support
8. controlled partial parallelism
9. deployment only when explicitly requested

Do not jump straight to Docker, Kubernetes, or cluster-specific work unless the user explicitly asks for it.

## When to use

Use this skill when Codex needs to:

- optimise peak memory use or repeated full-table materialisation;
- simplify module boundaries or orchestration;
- refactor one stage of ingest, packet extraction, flow construction, sampling, metrics, plotting, runtime, or logging;
- add or improve execution logs, run metadata, or user-visible progress reporting;
- enable plotting modes or plotting automation;
- introduce safe partial parallelism after the shared baseline semantics are frozen;
- update code and hot documentation together.

## Guardrails

Do not let performance work redefine the methodology.

The following must remain fixed unless the user explicitly requests a methodological change:

- the `1:1` baseline as ground truth;
- the default `15-second` inactivity timeout;
- the chosen flow key for a given experiment;
- metric formulas and unit conventions;
- dataset acceptance rules.

Do not replace a validated CPU reference path with an unvalidated accelerated path.

Do not introduce parallelism that weakens baseline consistency or reproducibility.

## Resource-aware rules

Assume the local development target is memory-constrained relative to packet-scale data.

Therefore:

- prefer streaming, chunked, or aggregate-first processing over repeated full in-memory materialisation;
- avoid keeping multiple large packet-level tables alive at once unless clearly justified;
- prefer one dataset at a time and one frozen baseline at a time;
- treat packet-level intermediates as optional where practical;
- prefer serial baseline construction before parallel work;
- parallelise across files or rates only after the shared methodology contract is frozen.

## Working mode

Treat pipeline work as an iterative sequence, not a one-shot rewrite.

Preferred loop:

1. inspect the relevant files and current stage boundaries;
2. identify one stage, one bottleneck, one interface, or one behavioural gap to change;
3. implement the smallest correct change;
4. validate immediately with focused tests or a small local run;
5. summarise what changed, what passed, what failed, and what remains;
6. only then move to the next stage.

For large tasks, keep the scope to one clean slice, such as:

- packet extraction memory use;
- baseline-flow construction refactor;
- sampled-rate orchestration;
- plotting stage enablement;
- logging/runtime integration;
- safe parallel execution of independent rates.

## Validation expectations

Whenever this skill changes code:

- run focused tests for the affected stage;
- run a small local example when practical;
- state whether the change is semantic, structural, operational, or performance-only;
- note any remaining memory-risk or correctness-risk areas.

Whenever this skill changes behaviour, also update the relevant document under `docs/hot/`.

## Multi-agent pattern

When multi-agent mode is enabled and the task is large enough, a good split is:

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

## Expected outputs

A successful run of this skill should usually produce:

- one scoped code change;
- one validation result;
- one concise note about remaining risks;
- one matching documentation update when behaviour or workflow expectations changed.

## Common failure cases

Avoid these mistakes:

- optimising before confirming methodology;
- parallelising baseline reconstruction too early;
- introducing repeated full-table rereads when a smaller derived artefact would suffice;
- hiding assumptions in hard-coded constants;
- mixing packets and bytes without explicit labels;
- enabling logging in a way that obscures stage boundaries;
- doing a wide repo rewrite when one stage-level refactor was enough;
- changing architecture without updating the hot documents.