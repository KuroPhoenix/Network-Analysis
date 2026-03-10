# Shared Module Maintenance

## Usage notes

- Keep methodology-sensitive defaults visible here rather than scattering them across stage modules.
- Prefer explicit enums, dataclasses, or similarly inspectable structures over hidden constants.

## Maintenance guidelines

- Update this module first when adding a new stage-level config parameter or shared schema.
- Review downstream modules after any change to timeouts, flow keys, size basis labels, or output-path conventions.

## Operational caveats

- Silent drift between shared definitions and stage-local assumptions would create methodology bugs, so treat mismatches as defects.

## Recommendations for future work

- Add stricter schema validation once real packet and flow artefacts exist.
- Add fixtures that validate config normalisation and shared defaults.
