---
name: flow-sampling-evaluator
description: Evaluate full-trace PCAP or PCAPNG files against one or more 1:X packet-sampling rates by reconstructing flow records from packets and measuring flow-level detection and estimation accuracy. Use when Codex needs to design, run, document, or review packet-sampling experiments, compare every sampled result to a 1:1 baseline, or report flow metrics such as detection rate, size, duration, sending rate, and distortion factors.
---

# Flow Sampling Evaluator

## Overview

Use this skill to analyze packet sampling experiments where a full trace is the baseline and one or more `1:X` packet-sampling rates must be evaluated against it.

Treat the `1:1` case as ground truth. Keep the flow inactivity timeout at `15 seconds` unless the user explicitly overrides it. Reconstruct sampled flow records from sampled packets only. Treat any flow present in the baseline but absent in a sampled trace as `undetected`.

## Required Inputs

Provide or identify these inputs before computing results:

- one full-trace `PCAP` or `PCAPNG` file for the `1:1` baseline;
- one or more packet-sampling rates such as `1:10`, `1:100`, or one sampled trace per rate only when its provenance from the same full trace is clear;
- one explicit flow key; if the user does not specify one, choose a standard directional 5-tuple and state that choice;
- one inactivity timeout; default to `15 seconds` unless the user explicitly requests a different value;
- one clear size basis: `packets`, `bytes`, or both.

State these experiment settings in the output:

- baseline file name and sampled file names or sampling procedure;
- flow key definition;
- inactivity timeout;
- sampling method used to obtain each `1:X` result;
- size basis and byte definition if bytes are used;
- random seed if random sampling is used.
- provenance link between each sampled trace and the baseline capture when sampled traces are supplied directly.

## Usage Steps

1. Build baseline flows from the full trace using the chosen flow key and the baseline inactivity timeout of `15 seconds` unless overridden.
2. Freeze the shared baseline, timeout, flow key, unit basis, and metric formulas before parallel work begins.
3. For each `1:X` rate, either derive the sampled packet stream from the baseline or load a sampled trace whose provenance from that baseline is clear.
4. Reconstruct sampled flows from sampled packets only. Do not infer missing packets from the baseline and do not scale baseline flow records directly.
5. Match each sampled result against the same shared `1:1` baseline using the same flow key and the same timeout policy.
6. Mark every baseline flow with no corresponding sampled flow as `undetected`.
7. Compute all requested metrics for each `1:X` result against the `1:1` baseline. Do not compare `1:100` to `1:10`; compare both to `1:1`.
8. Report per-rate summaries and, when useful, a per-flow comparison table.

## Multi-Agent Pattern

When multi-agent mode is enabled, build the `1:1` baseline once and keep it fixed.

- The main agent should own baseline construction and freeze the methodology contract before delegating.
- One worker per `1:X` rate is appropriate only after the baseline, timeout, flow key, unit basis, and formulas are fixed.
- Every worker must compare only against that shared baseline.
- Do not let separate workers rebuild the baseline independently or reinterpret the metric definitions.

## Metric Definitions

Use the same unit basis on both sides of every formula.

- `flow detection rate = detected baseline flows / total baseline flows`
- `flow size estimation = sampled flow size estimate compared to baseline flow size`
- `flow duration = last packet timestamp - first packet timestamp` within the reconstructed flow record
- `flow sending rate = flow size / flow duration`
- `flow size overestimation factor = sampled estimated size / baseline size`
- `flow duration underestimation factor = sampled estimated duration / baseline duration`
- `flow sending rate overestimation factor = flow size overestimation factor / flow duration underestimation factor`

Interpret the duration ratio carefully:
- values below `1` indicate underestimation;
- values near `1` indicate closer agreement.

Apply these rules while computing metrics:

- Compute detection rate over all baseline flows.
- Compute size, duration, and sending-rate estimation only from reconstructed sampled flows matched to baseline flows.
- Keep undetected baseline flows in the detection calculation even when estimation metrics are undefined for them.
- Handle zero-duration flows explicitly. If duration is `0`, mark sending rate and any ratio using that denominator as `undefined`, `NA`, or another clearly labeled non-numeric value.

## Packet and Byte Labeling

Label every size and rate result with its basis.

- Use `packets` when counting packets per flow.
- Use `bytes` only when the byte definition is explicit, such as captured frame bytes, IP bytes, or payload bytes.
- Avoid mixed labels such as `size` or `rate` without units.
- If both packet-based and byte-based results are reported, keep them in separate columns or clearly named metrics.

## Reproducibility Guidance

Make the experiment easy to rerun and audit.

- Use the same flow key and inactivity timeout across the baseline and every sampled result unless the user explicitly asks for a sensitivity study.
- Record the exact sampling rule for each `1:X` result. If sampling has randomness, record the random seed.
- Record the exact size definition used for bytes.
- Record how zero-duration flows and undefined ratios are handled.
- Keep output filenames or table labels deterministic, for example by including trace name, sampling rate, flow key, timeout, and unit basis.
- State whether the sampled traces were provided directly or generated during the analysis.
- Treat externally supplied sampled traces as comparators only, never as ground truth.

## Expected Outputs

Produce reproducible outputs for each `1:X` rate:

- one summary table with the rate, baseline flow count, detected flow count, undetected flow count, and flow detection rate;
- one metric table or section covering flow size estimation, flow duration, flow sending rate, flow size overestimation factor, flow duration underestimation factor, and flow sending rate overestimation factor;
- one clear statement that each sampled result is compared against the `1:1` baseline;
- one metadata block listing the baseline trace, sampled trace or sampling rule, flow key, timeout, size basis, and any override choices.

Add a per-flow output when the task calls for drill-down analysis:

- flow identifier or matching key;
- baseline size, duration, and sending rate;
- sampled size, duration, and sending rate;
- detection status;
- per-flow factors or errors.

## Common Failure Cases

Watch for these errors and correct them before reporting results:

- comparing sampled traces to each other instead of comparing each one to the `1:1` baseline;
- treating sampled flows as scaled copies of baseline flows instead of reconstructing them from sampled packets only;
- dropping baseline flows that are absent in the sampled trace instead of marking them as undetected;
- using a timeout other than `15 seconds` without documenting an explicit override;
- changing the flow key or directionality between the baseline and sampled traces;
- reporting `size` or `rate` without saying whether the basis is packets or bytes;
- mixing different byte definitions across files or metrics;
- failing to handle zero-duration flows and divide-by-zero cases explicitly.
