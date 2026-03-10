"""Minimal CLI for validating and planning the MVP pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from network_analysis.pipeline.driver import render_pipeline_plan, run_pipeline
from network_analysis.shared.config import ConfigError, load_pipeline_config
from network_analysis.stages.base import StageNotImplementedError


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(
        prog="network-analysis",
        description="Local-first pipeline CLI skeleton for packet-trace flow analysis.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/pipeline.sample.yaml"),
        help="Path to the pipeline configuration file.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "validate-config",
        help="Load the config and print the resolved methodology and paths.",
    )
    subparsers.add_parser(
        "plan",
        help="Print the named stage plan without executing any stage logic.",
    )
    run_parser = subparsers.add_parser(
        "run",
        help="Run the pipeline. In Stage 1 only --dry-run is expected to succeed.",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the execution plan without invoking stage implementations.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint used by tests and console scripts."""

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_pipeline_config(args.config)
        if args.command == "validate-config":
            print("\n".join(config.summary_lines()))
            return 0
        if args.command == "plan":
            print(render_pipeline_plan(config))
            return 0
        if args.command == "run":
            run_pipeline(config, dry_run=args.dry_run)
            if args.dry_run:
                print(render_pipeline_plan(config))
            return 0
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        return 2
    except StageNotImplementedError as exc:
        print(f"Stage implementation pending: {exc}")
        return 3

    parser.error(f"Unsupported command: {args.command}")
    return 2


def main_entry() -> None:
    """Console-script wrapper."""

    raise SystemExit(main())

