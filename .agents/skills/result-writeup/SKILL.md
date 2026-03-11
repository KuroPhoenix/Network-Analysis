---
name: result-writeup
description: Turn completed flow-sampling analysis outputs into a consistent report-ready summary for this repository. Use when writing concise results sections or summary paragraphs that state the dataset, baseline condition, tested sampling rate or rates, the direction of change for flow detection, flow size, flow duration, flow sending rate, and the three derived distortion factors, while separating observations from interpretation and avoiding unsupported claims.
---

# Result Writeup

## Overview

Use this skill after the flow-sampling analysis is already complete and the computed outputs are available.

Write a report-ready summary that states what was tested and what changed, without inventing causes, trends, or significance that are not directly supported by the results.

Default to single-agent execution.

If delegation is needed, use a `writer + claim-checker` split rather than multiple independent writers.

## Required inputs

Collect these items before writing:

- dataset name or trace identifier;
- baseline condition, normally the `1:1` case;
- tested sampling rate or rates;
- flow key and inactivity timeout when they differ from repo defaults or when the summary must stand on its own;
- computed results for flow detection, flow size, flow duration, and flow sending rate;
- computed distortion factors for flow size overestimation, flow duration underestimation, and flow sending rate overestimation;
- any unit labels needed to avoid ambiguity, such as packets versus bytes.

If one of these is missing, keep the missing item visible in the output.

## Usage steps

1. Read the completed analysis outputs and confirm that every sampled result is compared against the stated baseline condition.
2. Extract the dataset name, baseline condition, and tested sampling rate or rates exactly as reported.
3. For each sampled rate, identify the reported direction of change for flow detection, flow size, flow duration, and flow sending rate.
4. Record the three derived distortion factors exactly as computed.
5. Write an `Observations` section that states only what the computed results show.
6. Write an `Interpretation` section only if the data supports a restrained interpretation.
7. Add a `Limits` note if support is incomplete or the outputs are ambiguous.

## Writing rules

- state the dataset first;
- state the baseline condition explicitly;
- state every tested sampling rate included in the summary;
- include the flow key or inactivity timeout when they are non-default or when omission would make the comparison ambiguous;
- preserve the metric names instead of replacing them with vague synonyms;
- keep packet-based and byte-based results clearly labelled;
- treat flow detection specially: `1:1` should match the baseline, and sampled rates should normally match or fall below the baseline;
- if a sampled detection rate exceeds the baseline, flag a likely bug, denominator mismatch, or definition error instead of calling it an improvement;
- do not imply causation unless the computed results directly support it;
- do not generalise beyond the dataset and rates actually analysed.

## Output structure

Use this structure unless the user asks for a different report format:

- `Context:` dataset, baseline condition, tested sampling rate or rates, and any non-default flow key or timeout
- `Observations:` direct statements of measured changes in flow detection, flow size, flow duration, flow sending rate, and the three derived distortion factors
- `Interpretation:` restrained explanation limited to what the observed results support
- `Limits:` missing rates, missing units, incomplete outputs, or other constraints that narrow the claim scope

## Observation guidance

Keep observations factual and metric-specific.

- state whether flow detection matched the baseline or fell below it;
- state whether flow size estimates increased, decreased, or stayed close to the baseline;
- state whether flow duration estimates became shorter, longer, or stayed close to the baseline;
- state whether flow sending rate estimates increased, decreased, or stayed close to the baseline;
- state the reported direction or magnitude of each distortion factor when available;
- when multiple rates are present, describe them rate by rate or as a compact progression.

## Interpretation guidance

Interpret only after the observations are complete.

- keep interpretation separate from the observation sentences;
- tie each interpretation back to one or more reported metrics;
- use cautious phrasing such as `these results indicate`, `within this dataset`, or `for the tested rates`;
- if the outputs only show directional change and not mechanism, say that the mechanism is not established by the current outputs;
- it is acceptable for the interpretation section to be one sentence or to say that no stronger interpretation is supported.

## Common failure cases

Avoid these write-up errors:

- mixing observations and interpretation in the same sentence;
- omitting the dataset, baseline condition, or tested sampling rates;
- normalising a sampled flow detection rate above the baseline instead of flagging it;
- describing only raw metrics while forgetting the three derived distortion factors;
- claiming causes or mechanisms that were not computed;
- generalising from one dataset to other environments;
- hiding missing units or unclear labels instead of flagging them as limits.