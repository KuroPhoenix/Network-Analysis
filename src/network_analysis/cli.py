"""CLI for the active dataset-root pipeline surface."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .base import ModuleNotImplementedError
from .config import ConfigError, V2ConfigError, load_dataset_template, load_run_config
from .runtime import override_datasets_root, render_active_plan, run_active_runs


def build_parser() -> argparse.ArgumentParser:
    """Build the active-architecture CLI parser."""

    parser = argparse.ArgumentParser(
        prog="network-analysis",
        description="Canonical local CLI for dataset-root packet-trace flow analysis.",
    )
    parser.add_argument(
        "--run-config",
        type=Path,
        default=Path("configs/run_conf.yaml"),
        help="Path to the active-architecture run config.",
    )
    parser.add_argument(
        "--dataset-template",
        type=Path,
        default=Path("configs/dataset_template.yaml"),
        help="Path to the active-architecture dataset template config.",
    )
    parser.add_argument(
        "--datasets-root",
        type=Path,
        help="Optional datasets-root override for the active architecture.",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        dest="active_plan",
        help="Print the active-architecture dataset plan without executing runs.",
    )
    parser.add_argument(
        "--validate-config",
        action="store_true",
        dest="active_validate",
        help="Load the active-architecture configs and print the resolved settings.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint used by tests and scripts."""

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        dataset_template = load_dataset_template(args.dataset_template)
        run_config = load_run_config(args.run_config)
        if args.datasets_root is not None:
            run_config = override_datasets_root(run_config, args.datasets_root)

        if args.active_validate:
            print("\n".join((*dataset_template.summary_lines(), *run_config.summary_lines())))
            return 0
        if args.active_plan:
            print(render_active_plan(run_config, dataset_template))
            return 0

        run_active_runs(run_config, dataset_template, dry_run=False)
        return 0
    except (ConfigError, V2ConfigError, FileNotFoundError, NotADirectoryError) as exc:
        print(f"Configuration error: {exc}")
        return 2
    except ModuleNotImplementedError as exc:
        print(f"Module implementation pending: {exc}")
        return 3


def main_entry() -> None:
    """Console-script wrapper."""

    raise SystemExit(main())
