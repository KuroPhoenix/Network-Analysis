---
name: dataset-vetting
description: Evaluate candidate network trace datasets for suitability in this repository by checking whether captures are full trace rather than pre-sampled, whether the file format is usable, whether timestamps support ground-truth reconstruction, whether the capture appears truncated or incomplete, whether the capture year satisfies repo policy, and whether metadata is sufficient to state the trace domain, losslessness, full wire-format support, and key caveats. Use when Codex needs to accept or reject a dataset for flow-level baseline analysis, compare several candidate datasets, or summarize uncertainty caused by incomplete documentation.
---

# Dataset Vetting

## Overview

Use this skill to screen candidate network trace datasets before they are used for baseline flow reconstruction or packet-sampling evaluation.

Produce a concise `accept` or `reject` assessment with reasons. When the dataset documentation is incomplete or ambiguous, include an explicit uncertainty section instead of filling gaps with assumptions.

## Required Checks

Assess each candidate dataset against these questions:

- Is the trace a full capture rather than an already sampled, aggregated, anonymized-into-flows, or otherwise transformed dataset?
- Is the file format usable in the current workflow, such as `PCAP` or `PCAPNG`, and is the trace readable without obvious corruption?
- Do packet timestamps appear precise, ordered enough, and complete enough for ground-truth flow reconstruction?
- Does the capture look truncated, partial, or operationally incomplete?
- Is the documented capture year `2020` or later, and if it is `2024` to `2026`, can that preference be noted?
- Is there enough metadata to state the trace domain, the main caveats, and whether losslessness and full wire-format packet data are documented?

If one of these cannot be answered directly, say so and carry the uncertainty into the final decision.

## Usage Steps

1. Gather the candidate files and any accompanying documentation, such as README text, dataset papers, filenames, capture notes, and provider metadata.
2. Identify the actual data representation. Reject datasets that are only flow records, summaries, feature tables, or pre-sampled exports when the repository needs packet-level ground truth.
3. Check the file format and practical usability. Confirm that the files are recognizable packet traces and note compression, splitting, corruption, or tooling constraints.
4. Inspect timestamp suitability. Look for per-packet timestamps, plausible resolution, monotonic progression with tolerable disorder, and enough fidelity to reconstruct flow starts, ends, and inactivity gaps.
5. Inspect completeness signals. Note whether the capture seems clipped at the beginning or end, contains unexplained gaps, missing directions, partial headers, or other signs that the trace is not a faithful full capture.
6. Review the dataset metadata. State the trace domain as precisely as the evidence allows, record the capture year, and note whether losslessness and full wire-format packet data are documented or unknown.
7. Emit a final `accept` or `reject` judgment with short reasons and an uncertainty section when evidence is incomplete.

## Decision Rules

Prefer `accept` only when the dataset is clearly usable for packet-level baseline reconstruction.

Accept when all of these are true:

- The dataset appears to be packet-level full trace data rather than pre-sampled or pre-aggregated data.
- The files are in a usable format for the repository workflow.
- Timestamps appear suitable for reconstructing ground-truth flows.
- No major evidence suggests the capture is truncated or fatally incomplete.
- The documented capture year is `2020` or later, or the year is unknown but that uncertainty is surfaced explicitly.
- The available metadata is sufficient to describe the trace domain, the major limitations, and whether losslessness and full wire-format support are documented.

Reject when any of these are true:

- The dataset is already sampled, aggregated into flows, or otherwise lacks raw packet-level evidence.
- The format is unusable, unreadable, or incompatible with the intended analysis.
- Timestamp quality is too poor or too ambiguous for defensible ground-truth reconstruction.
- The capture appears materially truncated, one-sided, or otherwise incomplete in ways that break baseline interpretation.
- The documented capture year is earlier than `2020`.
- Metadata is so sparse that the trace domain or major caveats cannot be stated with reasonable confidence.

Treat `2024` to `2026` as a preference, not a hard requirement. Mention that preference in the output when the evidence supports it.

## When many candidates exist

If the user presents several candidate datasets, compare them in a compact table before giving the final decision.
When multi-agent mode is enabled and the candidate set is large, one sub-agent per dataset is appropriate.
Keep the decision schema fixed across workers. Each worker should return:

- `Assessment`
- `Reasons`
- `Capture year`
- `Trace domain`
- `Capture support`
- `Main caveats`
- `Uncertainty`

Do not let different workers apply different acceptance standards.

## What to Look For

Use concrete evidence instead of vague impressions.

- Full-trace indicators: packet records, link-layer headers, continuous packet numbering, unsampled capture language, and documentation that describes passive capture rather than exports.
- Pre-sampled indicators: explicit `1:X` sampling notes, NetFlow/IPFIX style summaries, sampled packet products, or references to packet selection before release.
- Usable-format indicators: `pcap`, `pcapng`, standard compression around those files, readable headers, and timestamps visible at packet level.
- Timestamp concerns: second-only precision, constant or repeated timestamps across many packets, obvious resets, missing timestamps, or documentation that timestamps were synthesized.
- Truncation concerns: abrupt start or end, asymmetric directions, clipped headers, unexplained long gaps, missing packets implied by counters, or capture notes that mention overload or dropped traffic.
- Metadata sufficiency: source environment, capture context, capture year, anonymization notes, known packet loss, support for full wire-format packet data, and any release caveats affecting interpretation.

## Expected Output

Keep the final output short and decision-oriented.

- `Assessment:` `accept` or `reject`
- `Reasons:` 2 to 5 short bullets tied to the required checks
- `Capture year:` one concise statement, including whether the dataset meets the `2020+` rule and whether it falls in the preferred `2024` to `2026` window
- `Trace domain:` one concise statement, or `unknown` if evidence is insufficient
- `Capture support:` one short line stating whether losslessness and full wire-format packet data are documented, unknown, or contradicted
- `Main caveats:` one short list
- `Uncertainty:` one short section describing missing documentation, ambiguous evidence, or checks that could not be completed

Use explicit uncertainty wording such as `unknown`, `not documented`, `not verifiable from available files`, or `likely but unconfirmed`.

## Common Failure Cases

Avoid these mistakes while vetting datasets:

- Treating a flow-export dataset as if it were raw packet trace data.
- Assuming a trace is full capture because the filename looks plausible.
- Ignoring timestamp precision or ordering problems that would distort flow reconstruction.
- Accepting a trace without checking for clipping, missing directions, or release-time truncation.
- Forgetting the repository year policy or failing to surface when the year is unknown.
- Treating undocumented losslessness or undocumented full packet data as if they were confirmed properties.
- Reporting a confident trace domain when the documentation does not support it.
- Hiding missing evidence inside the reasons instead of surfacing it in a dedicated uncertainty section.
