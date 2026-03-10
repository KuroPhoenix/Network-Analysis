"""Documented schema contracts for the MVP pipeline artifacts."""

from .constants import PREFERRED_TABULAR_FORMAT
from .types import TableColumn, TableSchema

DATASET_REGISTRY_SCHEMA = TableSchema(
    name="dataset_registry",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("discovery_index", "int64", "Deterministic discovery order for raw files."),
        TableColumn("input_dir", "string", "Resolved raw input directory."),
        TableColumn("raw_glob", "string", "Discovery glob for raw capture files."),
        TableColumn("raw_file", "string", "Discovered raw capture or archive path."),
        TableColumn("raw_file_size_bytes", "int64", "Raw file size in bytes."),
        TableColumn("capture_format_hint", "string", "Capture format inferred from the file name.", required=False),
        TableColumn("compression_type", "string", "Compression wrapper inferred from the file name."),
        TableColumn("flow_key", "string", "Configured flow-key field order."),
        TableColumn(
            "inactivity_timeout_seconds",
            "int64",
            "Configured inactivity timeout used by downstream modules.",
        ),
        TableColumn("size_basis", "string", "Configured size basis selection."),
        TableColumn("byte_basis", "string", "Configured byte definition when bytes are requested."),
    ),
)

INGEST_MANIFEST_SCHEMA = TableSchema(
    name="ingest_manifest",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("source_discovery_index", "int64", "Deterministic raw-file discovery order."),
        TableColumn(
            "source_member_index",
            "int64",
            "Deterministic member order within a wrapper expansion.",
        ),
        TableColumn("source_file", "string", "Raw input file path."),
        TableColumn("archive_member_path", "string", "Archive member path when extracted from an archive.", required=False),
        TableColumn("staged_file", "string", "Immutable staged capture path."),
        TableColumn("staging_action", "string", "How the staged file was produced."),
        TableColumn("capture_format", "string", "Detected capture format."),
        TableColumn("compression_type", "string", "Detected compression wrapper."),
        TableColumn("source_sha256", "string", "SHA256 checksum of the source raw file."),
        TableColumn("staged_sha256", "string", "SHA256 checksum of the staged capture file."),
        TableColumn("source_size_bytes", "int64", "Raw input file size in bytes."),
        TableColumn("staged_size_bytes", "int64", "Staged capture size in bytes."),
    ),
)

PACKET_TABLE_SCHEMA = TableSchema(
    name="canonical_packet_table",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("source_discovery_index", "int64", "Deterministic raw-file discovery order."),
        TableColumn(
            "source_member_index",
            "int64",
            "Deterministic member order within a wrapper expansion.",
        ),
        TableColumn("source_file", "string", "Staged capture file path."),
        TableColumn("packet_index", "int64", "Deterministic dataset-wide packet index."),
        TableColumn("source_packet_index", "int64", "Packet position in the staged source capture."),
        TableColumn("timestamp_us", "int64", "Canonical UTC packet timestamp in microseconds."),
        TableColumn("timestamp", "datetime[us, UTC]", "Per-packet timestamp derived from the UTC microsecond value."),
        TableColumn("captured_len", "int64", "Captured packet length."),
        TableColumn(
            "wire_len",
            "int64",
            "Original on-wire packet length when the parser exposes it.",
            required=False,
        ),
        TableColumn("protocol", "string", "Transport or network protocol."),
        TableColumn("src_ip", "string", "Source IP address.", required=False),
        TableColumn("dst_ip", "string", "Destination IP address.", required=False),
        TableColumn("src_port", "int32", "Source transport port.", required=False),
        TableColumn("dst_port", "int32", "Destination transport port.", required=False),
        TableColumn("tcp_flags", "string", "TCP flags when applicable.", required=False),
        TableColumn(
            "flow_eligible",
            "bool",
            "Whether the packet has the full directional 5-tuple needed for flow reconstruction.",
        ),
        TableColumn(
            "flow_ineligible_reason",
            "string",
            "Why the packet cannot be used for flow reconstruction under the default directional 5-tuple.",
            required=False,
        ),
    ),
)

PACKET_EXTRACTION_MANIFEST_SCHEMA = TableSchema(
    name="packet_extraction_manifest",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("source_file_count", "int64", "Number of staged capture files processed."),
        TableColumn("total_packets", "int64", "Total packets observed across staged capture files."),
        TableColumn("flow_eligible_packets", "int64", "Packets eligible for default flow reconstruction."),
        TableColumn("flow_ineligible_packets", "int64", "Packets retained but excluded from flow reconstruction."),
        TableColumn("earliest_timestamp", "datetime[us, UTC]", "Earliest packet timestamp.", required=False),
        TableColumn("latest_timestamp", "datetime[us, UTC]", "Latest packet timestamp.", required=False),
    ),
)

BASELINE_FLOW_SCHEMA = TableSchema(
    name="baseline_flows",
    format=PREFERRED_TABULAR_FORMAT,
    columns=(
        TableColumn("dataset_id", "string", "Configured dataset identifier."),
        TableColumn("flow_id", "string", "Stable flow identifier."),
        TableColumn("src_ip", "string", "Source IP address for the configured directional flow key."),
        TableColumn("dst_ip", "string", "Destination IP address for the configured directional flow key."),
        TableColumn("src_port", "int32", "Source transport port for the configured directional flow key."),
        TableColumn("dst_port", "int32", "Destination transport port for the configured directional flow key."),
        TableColumn("protocol", "string", "Transport protocol for the configured directional flow key."),
        TableColumn("flow_sequence", "int64", "Per-flow-key sequence number after inactivity-based splitting."),
        TableColumn("start_ts", "datetime[us]", "First packet timestamp."),
        TableColumn("end_ts", "datetime[us]", "Last packet timestamp."),
        TableColumn("start_packet_index", "int64", "Dataset-wide packet index of the first packet in the flow."),
        TableColumn("end_packet_index", "int64", "Dataset-wide packet index of the last packet in the flow."),
        TableColumn("duration_seconds", "float64", "Flow duration in seconds."),
        TableColumn("packet_count", "int64", "Packet-count flow size."),
        TableColumn("byte_count", "int64", "Byte-count flow size using the configured byte basis."),
        TableColumn(
            "sending_rate_packets_per_second",
            "float64",
            "Packet-count sending rate. Undefined for zero-duration flows.",
            required=False,
        ),
        TableColumn(
            "sending_rate_bytes_per_second",
            "float64",
            "Byte-count sending rate. Undefined for zero-duration flows.",
            required=False,
        ),
        TableColumn(
            "size_basis",
            "string",
            "Configured size basis metadata for downstream metrics.",
        ),
        TableColumn("byte_basis", "string", "Configured byte definition used for byte-count metrics."),
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
