---
name: flow-sampling-evaluator
description: Evaluate full-trace PCAP or PCAPNG files against one or more 1:X packet-sampling rates by reconstructing flow records from packets and measuring flow-level detection and estimation accuracy. Use when designing, running, documenting, or reviewing packet-sampling experiments, always comparing each sampled result to a frozen 1:1 baseline under a fixed flow key, inactivity timeout, and unit basis.
---

# Flow Sampling Evaluator

## Overview

Use this skill to analyse packet-sampling experiments where a full trace is the baseline and one or more `1:X` packet-sampling rates must be evaluated against it.

Treat the `1:1` case as ground truth.

Keep the flow inactivity timeout at `15 seconds` unless the user explicitly overrides it.

Reconstruct sampled flow records from sampled packets only.

Treat any baseline flow absent in a sampled result as `undetected`.

## Required inputs

Provide or identify these inputs before computing results:

- one full-trace `pcap` or `pcapng` file for the `1:1` baseline;
- one or more packet-sampling rates such as `1:10`, `1:100`, or one sampled trace per rate only when provenance from the same full trace is clear;
- one explicit flow key; if unspecified, choose a standard directional 5-tuple and state that choice;
- one inactivity timeout; default to `15 seconds`;
- one clear size basis: `packets`, `bytes`, or both.

State these experiment settings in the output:

- baseline file name and sampled file names or sampling procedure;
- flow key definition;
- inactivity timeout;
- sampling method used to obtain each `1:X` result;
- size basis and byte definition if bytes are used;
- random seed if random sampling is used;
- provenance link between each sampled trace and the baseline capture when sampled traces are supplied directly.

## Usage steps

1. Build baseline flows from the full trace using the chosen flow key and inactivity timeout.
2. Freeze the shared baseline, timeout, flow key, unit basis, and metric formulas before any parallel work begins.
3. For each `1:X` rate, either derive the sampled packet stream from the baseline or load a sampled trace whose provenance from that baseline is clear.
4. Reconstruct sampled flows from sampled packets only.
5. Match each sampled result against the same shared `1:1` baseline.
6. Mark every baseline flow with no corresponding sampled flow as `undetected`.
7. Compute all requested metrics for each `1:X` result against the `1:1` baseline.
8. Report per-rate summaries and, when useful, a per-flow comparison table.

## Metric definitions

Use the same unit basis on both sides of every formula.

- `flow detection rate = detected baseline flows / total baseline flows`
- `flow size estimation = sampled flow size estimate compared to baseline flow size`
- `flow duration = last packet timestamp - first packet timestamp`
- `flow sending rate = flow size / flow duration`
- `flow size overestimation factor = sampled estimated size / baseline size`
- `flow duration underestimation factor = sampled estimated duration / baseline duration`
- `flow sending rate overestimation factor = flow size overestimation factor / flow duration underestimation factor`

Apply these rules:

- compute detection rate over all baseline flows;
- compute size, duration, and sending-rate estimation only from sampled flows matched to baseline flows;
- keep undetected baseline flows in the detection calculation;
- handle zero-duration flows explicitly and label undefined quantities clearly.

## Reproducibility guidance

- use the same flow key and inactivity timeout across the baseline and every sampled result unless the user explicitly requests a sensitivity study;
- record the exact sampling rule for each `1:X` result;
- record the random seed when randomness is used;
- record the exact byte definition when bytes are used;
- record how zero-duration flows and undefined ratios are handled;
- keep output filenames or table labels deterministic.

## Multi-agent pattern

When multi-agent mode is enabled:

- the main agent should own baseline construction;
- one worker per `1:X` rate is appropriate only after the baseline and methodology contract are frozen;
- every worker must compare only against that shared baseline;
- separate workers must not rebuild the baseline independently.

## Expected outputs

Produce reproducible outputs for each `1:X` rate:

- one summary table with baseline flow count, detected flow count, undetected flow count, and detection rate;
- one metric table covering flow size estimation, flow duration, flow sending rate, and the three distortion factors;
- one clear statement that each sampled result is compared against the `1:1` baseline;
- one metadata block listing the baseline trace, sampled trace or sampling rule, flow key, timeout, size basis, and any override choices.

## Common failure cases

Watch for these errors:

- comparing sampled traces to each other instead of comparing each one to `1:1`;
- treating sampled flows as scaled copies of baseline flows instead of reconstructing them from sampled packets;
- dropping baseline flows that are absent in the sampled trace instead of marking them as undetected;
- using a timeout other than `15 seconds` without documenting an explicit override;
- changing the flow key or directionality between baseline and sampled traces;
- reporting size or rate without saying whether the basis is packets or bytes;
- failing to handle zero-duration flows explicitly.