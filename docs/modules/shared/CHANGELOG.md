# Shared Module Changelog

## 2026-03-10

1. Purpose of modification: keep the shared contract aligned with the first executable baseline-flow module.
2. What changed: extended the documented baseline-flow schema to cover directional flow-key fields, inactivity-split sequencing, explicit packet and byte counts, and zero-duration-safe sending-rate columns.
3. Impact on other pipeline modules: flow construction, sampling, and metrics now share one documented baseline-flow contract instead of inferring fields ad hoc.
4. Required maintenance or follow-up updates: keep schema and path definitions aligned as sampled-flow reconstruction and metric tables are implemented.
