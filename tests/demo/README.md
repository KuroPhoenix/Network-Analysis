# Demo Artefacts

This directory documents the synthetic local demo used to validate the MVP without committing a raw capture file.

## Usage

1. Install the project dependencies so `dpkt` is available.
2. Run `python3 scripts/create_demo_capture.py` from the repository root.
3. Use `configs/demo.pipeline.yaml` as the pipeline config for the local end-to-end example.

## Demo Contract

- Dataset ID: `demo_trace`
- Raw input directory: `data/raw/demo_trace`
- Capture file name: `demo_trace.pcap`
- Flow key: directional 5-tuple
- Inactivity timeout: `15 seconds`
- Size basis: `packets`
- Byte definition if later requested: `captured_len`
- Sampling method: deterministic systematic sampling
- Demo rates: `1:2` and `1:3`
