---
name: result-writeup
description: Turn completed flow-sampling analysis outputs into a consistent report-ready summary for this repository. Use when Codex needs to write concise results sections or summary paragraphs that state the dataset, baseline condition, tested sampling rate or rates, the direction of change for flow detection, flow size, flow duration, flow sending rate, and the three derived distortion factors, while separating observations from interpretation and avoiding unsupported claims.
---

# Result Writeup

## Overview

Use this skill after the flow-sampling analysis is already complete and the computed outputs are available.

Write a report-ready summary that states what was tested and what changed, without inventing causes, trends, or significance that are not directly supported by the results.
Default to single-agent execution. If delegation is needed, use a `writer + claim-checker` split rather than multiple independent writers.

## Required Inputs

Collect these items before writing:

- dataset name or trace identifier;
- baseline condition, normally the `1:1` case;
- tested sampling rate or rates, such as `1:10`, `1:100`, or a full rate list;
- flow key and inactivity timeout when they differ from the repo defaults or when the summary must stand on its own;
- computed results for flow detection, flow size, flow duration, and flow sending rate;
- computed distortion factors for flow size overestimation, flow duration underestimation, and flow sending rate overestimation;
- any unit labels needed to avoid ambiguity, such as packets versus bytes.

If one of these is missing, say that the writeup cannot fully characterize the result and keep the missing item visible in the output.

## Usage Steps

1. Read the completed analysis outputs and confirm that every sampled result is compared against the stated baseline condition.
2. Extract the dataset name, baseline condition, and tested sampling rate or rates exactly as reported.
3. For each sampled rate, identify the reported direction of change for:
   - flow detection
   - flow size
   - flow duration
   - flow sending rate
4. Record the three derived distortion factors exactly as computed:
   - flow size overestimation factor
   - flow duration underestimation factor
   - flow sending rate overestimation factor
5. Write an `Observations` section that states only what the computed results show.
6. Write an `Interpretation` section only if the data supports a restrained interpretation. Keep it limited to direct implications of the measured results.
7. If support is weak or incomplete, keep the interpretation short and explicitly note the limitation.

If multi-agent mode is enabled, use this delegation pattern:

- one writer agent drafts the summary from the fixed results;
- one claim-checker agent audits unsupported interpretation, missing context, and wording that exceeds the evidence;
- the main agent consolidates the final version.

## Writing Rules

Keep the summary consistent and defensible.

- State the dataset first.
- State the baseline condition explicitly.
- State every tested sampling rate included in the summary.
- Include the flow key or inactivity timeout when they are non-default or when omission would make the comparison ambiguous.
- Describe change direction with precise language such as `decreased`, `increased`, `shorter`, `longer`, `higher`, `lower`, or `no clear change in the reported results`.
- Preserve the metric names instead of replacing them with vague synonyms.
- Keep packet-based and byte-based results clearly labeled.
- Treat flow detection specially: `1:1` should match the baseline, and sampled rates should normally match or fall below the baseline. If a sampled detection rate exceeds the baseline, flag a likely bug, denominator mismatch, or definition error instead of calling it an improvement.
- Do not imply causation unless the computed results directly support it and the task specifically calls for that claim.
- Do not generalize beyond the dataset and rates actually analyzed.
- Do not claim statistical significance, robustness, or practical impact unless those were computed separately and provided as inputs.

## Output Structure

Use this structure unless the user asks for a different report format:

- `Context:` dataset, baseline condition, tested sampling rate or rates, and any non-default flow key or timeout
- `Observations:` direct statements of measured changes in flow detection, flow size, flow duration, flow sending rate, and the three derived distortion factors
- `Interpretation:` restrained explanation limited to what the observed results support
- `Limits:` missing rates, missing units, incomplete outputs, or other constraints that narrow the claim scope

## Observation Guidance

Keep observations factual and metric-specific.

- State whether flow detection matched the baseline or fell below it. If a sampled rate exceeds the baseline, flag it as a likely bug or definition mismatch.
- State whether flow size estimates increased, decreased, or stayed close to the baseline.
- State whether flow duration estimates became shorter, longer, or stayed close to the baseline.
- State whether flow sending rate estimates increased, decreased, or stayed close to the baseline.
- State the reported direction or magnitude of each distortion factor when available.
- When multiple sampling rates are present, describe them rate by rate or in a compact progression from lighter to heavier sampling.

## Interpretation Guidance

Interpret only after the observations are complete.

- Keep interpretation separate from the observation sentences.
- Tie each interpretation back to one or more reported metrics.
- Use cautious phrasing such as `these results indicate`, `within this dataset`, or `for the tested rates`.
- If the results only show directional change and not mechanism, say that the mechanism is not established by the current outputs.
- If the outputs are purely descriptive, it is acceptable for the interpretation section to be one sentence or to say that no stronger interpretation is supported.

## Expected Output

Produce a concise summary that a report can reuse with minimal editing.

- one short context block naming the dataset, baseline condition, tested rate or rates, and any non-default flow key or timeout;
- one short observations paragraph or bullet list covering the four primary metrics and the three distortion factors;
- one short interpretation paragraph that stays within the evidence;
- one short limits note when the available outputs are incomplete or ambiguous.

## Common Failure Cases

Avoid these writeup errors:

- mixing observations and interpretation in the same sentence;
- omitting the dataset, baseline condition, or tested sampling rates;
- normalizing a sampled flow detection rate above the baseline instead of flagging it as an error condition;
- describing only raw metrics while forgetting the three derived distortion factors;
- claiming causes or mechanisms that were not computed;
- generalizing from one dataset to other environments or traffic domains;
- hiding missing units or unclear labels instead of flagging them as limits;
- writing stronger conclusions than the computed results support.
