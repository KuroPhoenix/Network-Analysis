"""CLI for dataset-folder batch execution."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .batch_runner import clean_batch_outputs, render_batch_plan, run_batch
from .shared.batch_config import BatchConfigError, load_batch_config
from .shared.config import ConfigError


def build_parser() -> argparse.ArgumentParser:
    """Build the batch CLI parser."""

    parser = argparse.ArgumentParser(
        prog="network-analysis-batch",
        description="Batch runner that scans dataset folders and runs the local pipeline once per dataset folder.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/datasets.batch.yaml"),
        help="Path to the batch-runner configuration file.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "validate-config",
        help="Load the batch config and print the resolved settings.",
    )
    subparsers.add_parser(
        "plan",
        help="Print the resolved dataset-folder batch plan without executing runs.",
    )
    subparsers.add_parser(
        "clean",
        help="Remove generated staged, processed, and results artifacts for the planned dataset runs.",
    )
    run_parser = subparsers.add_parser(
        "run",
        help="Run the local pipeline once per discovered dataset folder.",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve the batch plan without invoking pipeline runs.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint used by scripts and tests."""

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_batch_config(args.config)
        if args.command == "validate-config":
            print("\n".join(config.summary_lines()))
            return 0
        if args.command == "plan":
            print(render_batch_plan(config))
            return 0
        if args.command == "clean":
            cleanup_summaries = clean_batch_outputs(config)
            for summary in cleanup_summaries:
                if summary.removed_paths:
                    print(
                        f"[clean] {summary.run_id}: removed "
                        + ", ".join(str(path) for path in summary.removed_paths)
                    )
                else:
                    print(f"[clean] {summary.run_id}: nothing to remove")
            return 0
        if args.command == "run":
            run_batch(config, dry_run=args.dry_run)
            if args.dry_run:
                print(render_batch_plan(config))
            return 0
    except (BatchConfigError, ConfigError) as exc:
        print(f"Batch configuration error: {exc}")
        return 2

    parser.error(f"Unsupported command: {args.command}")
    return 2


def main_entry() -> None:
    """Console-script wrapper."""

    raise SystemExit(main())
