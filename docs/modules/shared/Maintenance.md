# Shared Module Maintenance

## Usage notes

- Keep methodology-sensitive defaults visible here rather than scattering them across pipeline modules.
- Prefer explicit enums, dataclasses, or similarly inspectable structures over hidden constants.
- Keep artifact-path conventions centralised here so module code does not drift into hard-coded filesystem assumptions.

## Maintenance guidelines

- Update this module first when adding a new module-level config parameter or shared schema.
- Review downstream modules after any change to timeouts, flow keys, size basis labels, byte basis, or output-path conventions.
- Review ingest and packet extraction together whenever provenance-order schema fields or canonical timestamp fields change.
- Re-check schema columns against real module outputs whenever a previously placeholder module becomes executable.
- Keep sampling and metrics schemas aligned whenever the matching rule or rate-estimation columns change.

## Operational caveats

- Silent drift between shared definitions and module-local assumptions would create methodology bugs, so treat mismatches as defects.

## Recommendations for future work

- Add stricter schema validation once later flow, sampling, and metric artefacts exist.
- Add fixtures that validate config normalisation, byte-basis handling, and artifact-path resolution together.
