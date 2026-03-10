# Network-Analysis
Repo for network analysis, the research result of Chia-Chen Hsieh in 交大資工專題 2026. Instructing professor: Shie-Yuan Wang （王協源）
## Project Goals

This study uses full-trace network packet captures as ground truth to evaluate how packet sampling affects the completeness and accuracy of reconstructed flow records. Using a fixed 15-second flow inactivity timeout, the study compares full-trace and sampled flow records in terms of flow detection rate, flow size estimation, flow duration, and flow sending rate. The objective is to show, through direct comparison with ground truth, how sampling can both miss existing flows and distort the measurements of detected flows, thereby motivating the need for high-precision full-flow monitoring on a P4 switch.

In other words, this study serves as the empirical evaluation component of a broader research effort. While the actual P4-based monitoring system is being designed and implemented by other members of the team, my role is to use real full-trace network captures to show why complete flow monitoring is necessary in practice. This matches the paper’s general methodology and motivation: first generate complete and accurate flow records from the trace as ground truth, then compare other monitoring outcomes against that ground truth, while showing that sampling can reduce both completeness and accuracy of flow records.

## Project Overview

My instructing professor (professor for short) is doing a research with the aim of being able to capture full traces of several switches/routers with a single P4 switch. My other colleagues are working on the system itself, including

- Actual implementation of the architecture.

- Process Monitoring

- Capturing packets, and subsequently processing them.

To assess the impacts of their work, they need real-life network trace examples to illustrate why their research goal is of significance. Therefore, my part is the following:

I need to collect some full traces from external sources, preferably from diverse sources such as campus networks, national bandwidth networks, and data center networks. I need to assess some flow metrics under different flow sample rates.

For each accepted trace, the analysis should follow a ground-truth-first design. That is, the full trace is first processed to reconstruct the complete set of flow records, and these full-trace flow records are then treated as the reference baseline. After that, sampled flow records under different sampling rates are reconstructed from the same trace and compared directly against the full-trace baseline, rather than being interpreted on their own. This is the same core evaluation logic used in the paper.

These metrics include:

- Flow size estimation

- Flow duration

- Flow sending rate

- Flow detection rate

The logic behind these metrics is as follows:

Under different flow sampling rates,

- Some real flows may not be detected at all. Therefore, flow detection rate is expected to fall below the full-trace baseline as sampling becomes sparser, though measured results must still be reported from the data.

- Even if a flow is detected, its sampled flow record may still deviate from the actual flow record.

- Flow size is expected to tend towards overestimation under the current sampled-size definition, because the estimated size = sampling rate × packets caught.

- Flow duration is expected to tend towards underestimation, because sampled packets may fail to capture the true start time and end time of the actual flow.

- Flow sending rate is therefore expected to tend towards overestimation, as sending rate = size / duration.

Therefore, some derivative metrics can be formulated as such:

- Flow size overestimation factor

- Flow duration underestimation factor

- Flow sending rate overestimation factor

The overall purpose of using these metrics is to capture the two central problems caused by sampling: completeness and accuracy. Flow detection rate measures whether a real flow is observed at all. Flow size estimation, flow duration, and flow sending rate measure whether the resulting sampled flow record still resembles the true flow record when only sampled packets are available. This is consistent with the paper’s evaluation logic, which distinguishes between whether a flow is detected and whether the exported flow data remains correct relative to the ground truth.

These are expected trends under this evaluation framework, not universal laws. The measured results from each trace and each sampling rate must still be reported exactly as observed.

## Implementation

We need to specify a flow interval to determine how long a flow can be "disconnected" while still being classified as the same flow. The current scheme sets the interval at 15s. As long as the flow does not disconnect for more than 15s, it is still considered a normal flow. If the gap between packets of the same flow exceeds 15s, then the current flow record should be considered finished, and any later packets should be treated as belonging to a new flow. This rule needs to remain fixed across all experiments so that the difference between the 1:1 case and the 1:X case is caused by sampling itself rather than by inconsistent flow termination rules. This is also consistent with the paper, which uses a 15-second idle timeout as the default NetFlow setting.

### Methodology defaults

- Default flow key = standard directional 5-tuple unless another definition is explicitly specified.
- Default inactivity timeout = 15 seconds unless explicitly overridden.
- `1:1` is the ground-truth baseline.
- Each `1:X` case must be compared directly against the corresponding `1:1` baseline.
- Externally supplied sampled traces are not acceptable as ground truth. They may only be used as derived comparison artefacts when provenance from the same full trace is clear.

### 1:1 Sample rate

This is the full-trace baseline and should be treated as the ground truth case.

For flow size, simply accumulate the packets captured.

For flow duration, use the actual observed packet arrivals of the flow to determine its start time and end time.

Flow sending rate = size / duration

Flow detection rate = 100%

In other words, under the 1:1 sample rate, every real flow in the trace should be detected, and the resulting flow records should be treated as the complete and accurate reference records for later comparison.

### 1:X Sample rate

Under the 1:X sample rate, all metrics must be evaluated against the 1:1 baseline rather than being interpreted on their own.

Flow size = Number of captured packets in a flow × sampling rate

Flow duration = Use the sampled packets to determine a flow's duration

Flow sending rate = sampled flow size / sampled flow duration

Flow detection = Number of flows detected under sampling scheme / Actual number of flows

A flow that exists in the full trace but has none of its packets captured under the sampling scheme should be treated as an undetected flow, rather than simply being ignored. This is important because otherwise the effect of sampling on completeness will be understated. This treatment is directly consistent with the paper’s methodology, where a flow existing in the trace but having no detected packets is treated as an undetected flow.

Flow size overestimation factor = sampled flow size / actual flow size

Flow duration underestimation factor = sampled flow duration / actual flow duration

Flow sending rate overestimation factor = flow size overestimation factor / flow duration underestimation factor

These derived metrics are meant to quantify how far a sampled flow record deviates from the corresponding full-trace flow record. The overall purpose is not only to see whether a flow is detected, but also to see whether the reconstructed flow record remains trustworthy after sampling.

## Local Setup

Create a virtual environment and install the local pipeline package plus test dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This repository uses a `src/` layout. Package-internal imports therefore use relative imports or `network_analysis...` imports, not `src.network_analysis...`. `pyrightconfig.json` points static analysis tools at `src/`, and `requirements.txt` includes an editable install of the local package for venv-based development.

## Dataset Expectations

1. Dataset should be diverse. That is, datasets should encompass data centre network traces, national link bandwidth network traces, campus network traces, etc (Any domain is accepted).

2. Dataset should be recent. Anything older than 2020 will not be considered. Datasets from 2024-2026 are preferred.

3. Dataset should be full-trace packet capture files in `PCAP` or `PCAPNG` format. Any sampled network trace datasets will not be considered as source datasets for baseline reconstruction.

4. Documented lossless packet capture is preferred.

5. Very accurate timestamps

6. Documented full wire-format packet data is preferred.


Among the above requirements, the most important methodological requirement for the analysis itself is that the trace must be full-traced rather than already sampled, because only then can it serve as the ground truth baseline for evaluating sampled flow records.
