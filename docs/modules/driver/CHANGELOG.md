# Driver Module Changelog

## 2026-03-10

1. Purpose of modification: turn the thin driver into a runnable local MVP entrypoint.
2. What changed: wired the implemented modules into the CLI run path, kept planning output aligned with the actual runnable module set, and made plotting conditional on `runtime.enable_plots`.
3. Impact on other pipeline modules: the full local path from raw captures through metrics now runs under one thin orchestration layer without moving business logic into the driver.
4. Required maintenance or follow-up updates: update this module documentation when module execution order, optional plotting behaviour, or run metadata changes.
