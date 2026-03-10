"""Repository-wide constant values for the MVP skeleton."""

from pathlib import Path

DEFAULT_FLOW_KEY_FIELDS = (
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "protocol",
)
DEFAULT_INACTIVITY_TIMEOUT_SECONDS = 15
DEFAULT_SAMPLING_RATES = (1,)
DEFAULT_SAMPLING_METHOD = "systematic"
DEFAULT_SIZE_BASIS = "packets"
DEFAULT_BYTE_BASIS = "captured_len"
PREFERRED_TABULAR_FORMAT = "parquet"
CANONICAL_SPEC_PATH = Path("docs/specs/pipeline-mvp.md")
COMPATIBILITY_SPEC_PATH = Path("docs/pipeline-mvp.md")
