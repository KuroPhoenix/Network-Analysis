---
name: dataset-vetting
description: Evaluate candidate network trace datasets for suitability in this repository by checking whether captures are full trace rather than pre-sampled, whether the file format is usable, whether timestamps support ground-truth reconstruction, whether the capture appears truncated or incomplete, whether the capture year satisfies repo policy, and whether metadata is sufficient to state the trace domain, losslessness, full wire-format support, and key caveats. Use when screening, comparing, accepting, or rejecting packet-trace datasets for baseline flow reconstruction.
---

# Dataset Vetting

## Overview

Use this skill to screen candidate datasets before they are used for baseline flow reconstruction or packet-sampling evaluation.

Produce a concise `accept` or `reject` assessment with explicit reasons.

When the documentation is incomplete or ambiguous, include an explicit uncertainty section instead of filling gaps with assumptions.

## Required checks

Assess each candidate against these questions:

- Is the trace a full packet capture rather than an already sampled, aggregated, or flow-export dataset?
- Is the file format usable in the current workflow, such as `pcap`, `pcapng`, or a standard compressed archive around them?
- Do packet timestamps appear precise and complete enough for ground-truth flow reconstruction?
- Does the capture look truncated, partial, asymmetric, or operationally incomplete?
- Is the documented capture year `2020` or later, and does it fall in the preferred `2024` to `2026` window?
- Is there enough metadata to state the trace domain, major caveats, and whether losslessness and full wire-format support are documented?

If one of these cannot be answered directly, say so.

## Usage steps

1. Gather the candidate files and all available documentation.
2. Identify the actual data representation.
3. Reject datasets that are only flow records, summaries, feature tables, or pre-sampled exports when packet-level ground truth is required.
4. Check practical file usability.
5. Inspect timestamp suitability for reconstructing flow starts, ends, and inactivity gaps.
6. Inspect completeness signals such as clipping, missing directions, missing headers, or unexplained gaps.
7. Record the trace domain, capture year, file format, and documented caveats.
8. Emit a final `accept` or `reject` judgment with short reasons and an uncertainty section when evidence is incomplete.

## Decision rules

Prefer `accept` only when the dataset is clearly usable for packet-level baseline reconstruction.

Accept when all of these are true:

- the dataset appears to be packet-level full-trace data;
- the files are usable in the repository workflow;
- timestamps appear suitable for defensible flow reconstruction;
- no major evidence suggests fatal incompleteness;
- the capture year is `2020+`, or the year is unknown but surfaced explicitly;
- the available metadata is sufficient to describe the trace domain and major limitations.

Reject when any of these are true:

- the dataset is already sampled, aggregated into flows, or otherwise lacks raw packet evidence;
- the format is unusable or incompatible with the intended workflow;
- timestamp quality is too poor or too ambiguous;
- the capture appears materially truncated or incomplete in a way that breaks baseline interpretation;
- the documented capture year is earlier than `2020`;
- the metadata is too sparse to state the trace domain or major caveats responsibly.

Treat `2024` to `2026` as a preference, not a hard requirement.

## Expected output

Keep the final output short and decision-oriented.

- `Assessment:` `accept` or `reject`
- `Reasons:` 2 to 5 short bullets tied to the required checks
- `Capture year:` one concise statement
- `Trace domain:` one concise statement, or `unknown`
- `Capture support:` one line stating whether losslessness and full wire-format support are documented, unknown, or contradicted
- `Main caveats:` one short list
- `Uncertainty:` one short section describing missing documentation or ambiguous evidence

## Common failure cases

Avoid these mistakes:

- treating a flow-export dataset as raw packet trace data;
- assuming a trace is full capture because the filename looks plausible;
- ignoring timestamp precision or ordering problems;
- accepting a trace without checking for clipping or missing directions;
- forgetting the repository year policy;
- treating undocumented losslessness as confirmed;
- hiding missing evidence instead of surfacing it explicitly.