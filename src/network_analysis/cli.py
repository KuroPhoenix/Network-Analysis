"""CLI for both the legacy MVP surface and the active dataset-root surface."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .modules.base import ModuleNotImplementedError
from .pipeline.driver import render_pipeline_plan, run_pipeline
from .shared.config import ConfigError, load_pipeline_config
from .runtime import override_datasets_root, render_active_plan, run_active_runs
from .shared.v2_config import V2ConfigError, load_dataset_template, load_run_config


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(
        prog="network-analysis",
        description="Local-first pipeline CLI for packet-trace flow analysis.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/pipeline.sample.yaml"),
        help="Path to the legacy MVP pipeline configuration file.",
    )
    parser.add_argument(
        "--run-config",
        type=Path,
        help="Path to the active-architecture run config.",
    )
    parser.add_argument(
        "--dataset-template",
        type=Path,
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
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Force the legacy MVP CLI interpretation even when active-architecture flags are present.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "validate-config",
        help="Load the config and print the resolved methodology and paths.",
    )
    subparsers.add_parser(
        "plan",
        help="Print the named module plan without executing any module logic.",
    )
    run_parser = subparsers.add_parser(
        "run",
        help="Run the local pipeline end to end. Plotting is skipped unless enabled in config.",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the execution plan without invoking module implementations.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint used by tests and console scripts."""

    parser = build_parser()
    args = parser.parse_args(argv)
    use_active_surface = not args.legacy and (
        args.run_config is not None
        or args.dataset_template is not None
        or args.datasets_root is not None
        or args.active_plan
        or args.active_validate
    )

    try:
        if use_active_surface:
            if args.command is not None:
                parser.error("Legacy subcommands cannot be combined with the active-architecture flags.")

            dataset_template = load_dataset_template(
                args.dataset_template or Path("configs/dataset_template.yaml")
            )
            run_config = load_run_config(args.run_config or Path("configs/run_conf.yaml"))
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

        if args.command is None:
            parser.error("A legacy subcommand or active-architecture flag is required.")

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
    except (ConfigError, V2ConfigError, FileNotFoundError, NotADirectoryError) as exc:
        print(f"Configuration error: {exc}")
        return 2
    except ModuleNotImplementedError as exc:
        print(f"Module implementation pending: {exc}")
        return 3

    parser.error(f"Unsupported command: {args.command}")
    return 2


def main_entry() -> None:
    """Console-script wrapper."""

    raise SystemExit(main())
