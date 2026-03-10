# Network-Analysis
Repo for network analysis, the research result of Chia-Chen Hsieh in 交大資工專題 2026. Instructing professor: Shie-Yuan Wang （王協源）

## Project Overview
My instructing professor (professor for short) is doing a research with the aim of being able to capture full traces of several switches/routers with a single P4 switch. My other colleagues are working on the system itself, including
* Actual implementation of the architecture.
* Process Monitoring
* Capturing packets, and subsequently processing them.

To assess the impacts of their work, they need real-life network trace examples to illustrate why their research goal is of significance. Therefore, my part is the following:

I need to collect some full traces from external sources, preferably from diverse sources such as campus networks, national bandwidth networks, and data center networks. I need to assess some flow metrics under different flow sample rates. 

These metrics include:
* Flow size estimation
* Flow duration
* Flow sending rate
* Flow detection rate

Under different flow sampling rates, 
* Flow size will be overestimated (As under different sampling schemes, the size = sample rate * packets caught)
* Flow duration will be underestimated
* Flow sending rate will therefore be overestimated (as sending rate =  size / duration)

Therefore, some derivative metrics can be formulated as such:
* Flow size overestimation factor
* Flow duration underestimation factor
* Flow Sending rate overestimation factor


## Implementation

We need to specify a flow interval to determine how long a flow can be "disconnected" while still being classified as the same flow. The current scheme sets the interval at 15s. As long as the flow does not disconnect for more than 15s, it is still considered a normal flow. 

### 1:1 Sample rate

For flow size, simply accumulate the packets captured. 

For flow duration, simply monitor each flow's packet arrival intervals.

Flow sending rate  = size / duration

Flow detection rate = 100%

### 1:X Sample rate

Flow size = Number of captured packets in a flow * sampling rate

Flow duration = Use the sampled packets to determine a flow's duration

Flow sending rate = sampled flow size / sampled flow duration

Flow detection = Number of flows detected under sampling scheme / Actual number of flows

Flow size overestimation factor = sampled flow size / actual flow size

Flow duration underestimation factor = sampled flow duration / actual flow duration

Flow sending rate overestimation factor = flow size overestimation factor / flow duration underestimation factor. 

## Dataset Expectations

1. Dataset should be diverse. That is, datasets should encompass data centre network traces, national link bandwidth network traces, campus network traces, etc (Any domain is accepted).
2. Dataset should be recent. Anything older than 2020 will not be considered. Datasets from 2024-2026 are preferred. 
3. Dataset should be full-traced pcap files. Any sampled network trace datasets will not be considered. 
4. Lossless packet capture
5. Very accurate timestamps
6. Full wire-format packet data
