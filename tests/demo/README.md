# Demo Artefacts

This directory documents the synthetic local demo used to validate the active dataset-root pipeline without committing a raw capture file.

## Usage

1. Install the project dependencies so `dpkt` is available.
2. Run `python3 scripts/create_demo_capture.py --overwrite` from the repository root.
3. Run `python3 scripts/run_pipeline.py --run-config configs/run_conf.yaml --datasets-root datasets/demo_root`.
4. The active runtime writes dataset-scoped outputs under `results/demo_trace/`.

## Demo Contract

- Dataset ID: `demo_trace`
- Dataset root: `datasets/demo_root`
- Raw input directory: `datasets/demo_root/demo_trace`
- Capture file name: `demo_trace.pcap`
- Flow key: directional 5-tuple
- Inactivity timeout: `15 seconds`
- Size basis: `packets`
- Byte definition if later requested: `captured_len`
- Sampling method: deterministic systematic sampling
- Demo rates: `1:2` and `1:3`
