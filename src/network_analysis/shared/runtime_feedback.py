"""Lightweight runtime feedback helpers for local pipeline execution."""

from __future__ import annotations

from contextlib import contextmanager
import os
import sys

try:  # pragma: no cover - tqdm is optional at import time
    from tqdm.auto import tqdm
except ImportError:  # pragma: no cover - fallback remains usable without tqdm
    tqdm = None


class _NoOpProgressBar:
    """Fallback progress-bar interface used when tqdm output is disabled."""

    def update(self, _: int = 1) -> None:
        return None

    def close(self) -> None:
        return None


class _TextProgressBar:
    """Text-only progress fallback when tqdm is unavailable."""

    def __init__(self, *, total: int, desc: str, unit: str) -> None:
        self.total = total
        self.desc = desc
        self.unit = unit
        self.current = 0
        print(
            f"[progress] {self.desc}: 0/{self.total} {self.unit}",
            file=sys.stderr,
            flush=True,
        )

    def update(self, increment: int = 1) -> None:
        self.current += increment
        print(
            f"[progress] {self.desc}: {self.current}/{self.total} {self.unit}",
            file=sys.stderr,
            flush=True,
        )

    def close(self) -> None:
        return None


def format_elapsed(seconds: float) -> str:
    """Render an elapsed duration in a compact human-readable form."""

    if seconds < 60:
        return f"{seconds:.2f}s"

    minutes, remaining_seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {remaining_seconds:05.2f}s"

    hours, remaining_minutes = divmod(int(minutes), 60)
    return f"{hours}h {remaining_minutes:02d}m {remaining_seconds:05.2f}s"


def progress_is_enabled() -> bool:
    """Return whether tqdm progress bars should be rendered for this run."""

    env_value = os.getenv("NETWORK_ANALYSIS_PROGRESS")
    if env_value is not None:
        return env_value.strip().lower() not in {"0", "false", "no", "off"}
    return sys.stderr.isatty()


def emit_runtime_event(message: str) -> None:
    """Emit a timing or progress event without corrupting active tqdm bars."""

    if tqdm is not None and progress_is_enabled():
        tqdm.write(message, file=sys.stderr)
        return

    print(message, file=sys.stderr, flush=True)


@contextmanager
def progress_bar(*, total: int, desc: str, unit: str, leave: bool = False):
    """Yield a tqdm progress bar when terminal output supports it."""

    if not progress_is_enabled():
        yield _NoOpProgressBar()
        return

    if tqdm is None:
        yield _TextProgressBar(total=total, desc=desc, unit=unit)
        return

    bar = tqdm(
        total=total,
        desc=desc,
        unit=unit,
        leave=leave,
        dynamic_ncols=True,
    )
    try:
        yield bar
    finally:
        bar.close()
