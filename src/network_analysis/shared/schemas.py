"""Documented schema contracts for the MVP pipeline artifacts."""

from network_analysis.shared.constants import PREFERRED_TABULAR_FORMAT
from network_analysis.shared.types import TableColumn, TableSchema

DATASET_REGISTRY_SCHEMA = TableSchema(
    name="dataset_registry",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("input_dir", "string", "Resolved raw input directory."),
        TableColumn("raw_glob", "string", "Discovery glob for raw capture files."),
        TableColumn("flow_key", "list[string]", "Configured flow-key field order."),
        TableColumn(
            "inactivity_timeout_seconds",
            "int64",
            "Configured inactivity timeout used by downstream stages.",
        ),
    ),
)

INGEST_MANIFEST_SCHEMA = TableSchema(
    name="ingest_manifest",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("source_file", "string", "Raw input file path."),
        TableColumn("staged_file", "string", "Immutable staged capture path."),
        TableColumn("capture_format", "string", "Detected capture format."),
        TableColumn("compression_type", "string", "Detected compression wrapper."),
        TableColumn("checksum", "string", "Optional checksum for reproducibility.", required=False),
    ),
)

PACKET_TABLE_SCHEMA = TableSchema(
    name="canonical_packet_table",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("source_file", "string", "Staged capture file path."),
        TableColumn("packet_index", "int64", "Packet position in source capture."),
        TableColumn("timestamp", "timestamp", "Per-packet timestamp."),
        TableColumn("captured_len", "int64", "Captured packet length."),
        TableColumn("wire_len", "int64", "On-wire packet length.", required=False),
        TableColumn("protocol", "string", "Transport or network protocol."),
        TableColumn("src_ip", "string", "Source IP address.", required=False),
        TableColumn("dst_ip", "string", "Destination IP address.", required=False),
        TableColumn("src_port", "int32", "Source transport port.", required=False),
        TableColumn("dst_port", "int32", "Destination transport port.", required=False),
        TableColumn("tcp_flags", "string", "TCP flags when applicable.", required=False),
    ),
)

BASELINE_FLOW_SCHEMA = TableSchema(
    name="baseline_flows",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("flow_id", "string", "Stable flow identifier."),
        TableColumn("start_ts", "timestamp", "First packet timestamp."),
        TableColumn("end_ts", "timestamp", "Last packet timestamp."),
        TableColumn("duration_seconds", "float64", "Flow duration in seconds."),
        TableColumn("packet_count", "int64", "Packet-count flow size.", required=False),
        TableColumn("byte_count", "int64", "Byte-count flow size.", required=False),
        TableColumn(
            "size_basis",
            "string",
            "Explicit size basis used for downstream metrics.",
        ),
    ),
)

SAMPLED_FLOW_SCHEMA = TableSchema(
    name="sampled_flows",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("sampling_rate", "int32", "Sampling rate expressed as X in 1:X."),
        TableColumn("flow_id", "string", "Matched or reconstructed flow identifier."),
        TableColumn("detected", "bool", "Whether the baseline flow was detected."),
        TableColumn(
            "estimated_packet_count",
            "int64",
            "Packet-size estimate after applying the sampling rule.",
            required=False,
        ),
        TableColumn(
            "estimated_byte_count",
            "int64",
            "Byte-size estimate after applying the sampling rule.",
            required=False,
        ),
        TableColumn("duration_seconds", "float64", "Sampled duration in seconds."),
    ),
)

METRIC_SUMMARY_SCHEMA = TableSchema(
    name="metric_summary",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("sampling_rate", "int32", "Sampling rate expressed as X in 1:X."),
        TableColumn("baseline_flow_count", "int64", "Ground-truth flow count."),
        TableColumn("detected_flow_count", "int64", "Detected baseline flow count."),
        TableColumn("undetected_flow_count", "int64", "Undetected baseline flow count."),
        TableColumn("flow_detection_rate", "float64", "Detected / baseline flow count."),
        TableColumn("size_basis", "string", "Explicit size basis used for the run."),
    ),
)

FLOW_METRIC_SCHEMA = TableSchema(
    name="flow_metrics",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("sampling_rate", "int32", "Sampling rate expressed as X in 1:X."),
        TableColumn("flow_id", "string", "Baseline flow identifier."),
        TableColumn("detection_status", "string", "Detected or undetected baseline flow."),
        TableColumn("baseline_size", "float64", "Ground-truth flow size.", required=False),
        TableColumn("sampled_size_estimate", "float64", "Sampled flow size estimate.", required=False),
        TableColumn("baseline_duration_seconds", "float64", "Ground-truth duration."),
        TableColumn("sampled_duration_seconds", "float64", "Sampled duration."),
        TableColumn("baseline_sending_rate", "float64", "Ground-truth sending rate.", required=False),
        TableColumn("sampled_sending_rate", "float64", "Sampled sending rate.", required=False),
        TableColumn(
            "flow_size_overestimation_factor",
            "float64",
            "Sampled size estimate divided by baseline size.",
            required=False,
        ),
        TableColumn(
            "flow_duration_underestimation_factor",
            "float64",
            "Sampled duration divided by baseline duration.",
            required=False,
        ),
        TableColumn(
            "flow_sending_rate_overestimation_factor",
            "float64",
            "Size factor divided by duration factor.",
            required=False,
        ),
    ),
)

