# Metrics Module Changelog

## 2026-03-10

1. Purpose of modification: implement the local MVP metrics module.
2. What changed: added baseline-vs-sampled metric computation, explicit detection-denominator handling, zero-duration-safe ratio handling, and Parquet summary plus per-flow metric outputs.
3. Impact on other pipeline modules: the driver can now run a full local analysis path through baseline construction, sampling, and metric computation without hidden comparison logic outside the module.
4. Required maintenance or follow-up updates: revisit the matching rule if the repo later introduces overlapping baseline-flow keys or alternative sampled-flow comparison semantics.
