# Git Workflow

## Purpose

This document defines the Git workflow for this repository.

The workflow is designed for a local-first, research-oriented codebase where:
- methodology stability matters more than rapid feature churn;
- code, specs, module docs, and tests must stay aligned;
- work is often done in small validated slices;
- Codex-assisted changes must remain reviewable and reversible.

This is not a heavy enterprise branching model.
It is a disciplined small-repo workflow.

---

## Core principles

### 1. Main must stay usable
`main` should remain in a runnable, reviewable state.

Do not push half-finished architecture changes, partial refactors, or broken validation states directly to `main` unless the change is truly trivial and low-risk.

### 2. Small validated slices
Prefer small, scoped branches and small commits over large opaque rewrites.

Each branch should normally correspond to one of:
- one bug fix
- one refactor slice
- one performance slice
- one documentation update set
- one plotting/logging/runtime slice

### 3. Code and docs move together
When a change affects architecture, behaviour, workflow, interfaces, or assumptions, update the relevant docs in the same branch.

At minimum, this may include:
- `AGENTS.md`
- `docs/hot/pipeline-v2.md`
- `docs/hot/git-workflow.md`
- module docs under `docs/modules/<module>/`

Do not let code drift ahead of the methodology or maintenance docs for long.

### 4. Validation before merge
A branch is not ready to merge just because the code looks reasonable.

Before merging, run the smallest validation set that can honestly support the change.

### 5. Preserve milestone clarity
Use Git history to distinguish:
- frozen architecture baselines
- active refactor work
- validated milestone transitions

Use tags for milestones, not duplicate source trees.

---

## Branch model

### Permanent branch
- `main`

`main` is the only permanent long-lived branch unless a future collaboration model requires more.

### Working branch categories

Use these prefixes:

- `feature/<scope>`
- `refactor/<scope>`
- `perf/<scope>`
- `fix/<scope>`
- `docs/<scope>`
- `chore/<scope>`

### Scope naming rule

Keep branch scopes short, concrete, and tied to one actual area.

Good examples:
- `refactor/flows-module`
- `perf/packet-extraction-memory`
- `feature/full-plotting`
- `fix/detection-denominator`
- `docs/pipeline-v2`
- `chore/gitignore-cleanup`

Avoid vague names such as:
- `update-stuff`
- `new-version`
- `changes`
- `codex-fixes`

### Branch size rule

A branch should usually cover one coherent topic.

Split work when:
- one branch starts touching unrelated modules;
- one branch mixes architecture changes with unrelated bug fixes;
- one branch becomes too large to validate honestly in one pass.

---

## Commit policy

### Commit frequency
Commit after each validated slice, not after every tiny edit and not only at the very end.

A good default is:
- checkpoint commit before risky refactor work;
- one or more validated commits during implementation;
- final cleanup commit only if it improves clarity.

### Commit message style

Use one of these prefixes:

- `feat:`
- `refactor:`
- `perf:`
- `fix:`
- `docs:`
- `test:`
- `chore:`

Examples:
- `refactor: merge flow construction and sampling boundaries`
- `perf: reduce packet extraction peak memory use`
- `fix: keep undetected flows in detection denominator`
- `docs: update pipeline-v2 for dataset-root execution model`
- `test: add zero-duration flow coverage`

### Commit content rule

A commit should ideally be one of:
- behavioural change
- structural refactor
- documentation sync
- validation/test addition
- cleanup with no semantic change

Do not mix unrelated purposes in one commit unless separation would make the history less clear.

---

## Change history policy

### Default rule
Use Git branches, commits, merge requests, or pull requests as the default routine changelog for this repository.

Manual changelog maintenance is not required for ordinary implementation work such as:
- fixes
- refactors
- performance work
- plotting, logging, or runtime additions
- test additions or updates
- routine file moves and renames

### What still requires manual documentation
Update repository docs when the change affects current:
- architecture
- methodology or metric definitions
- config schema or exposed parameters
- execution model
- output layout or result contracts
- milestone freeze state
- maintenance guidance future work depends on

Keep module `CHANGELOG.md` files for purpose-, architecture-, direction-, interface-, or milestone-driven notes.
Do not use them as routine per-change logs.

### Merge or PR description rule
If Git history is serving as the routine changelog, merge requests, pull requests, or merge descriptions should state:
- what changed
- why it changed
- what was validated
- whether docs were updated

Prefer squash merge when that produces one clear, reviewable history entry for the branch.

---

## Merge policy

### Default merge target
All working branches merge back into `main`.

### Preferred merge style
Prefer **squash merge** when a branch contains many noisy intermediate commits.

Prefer **regular merge** only when the branch history itself is meaningful and reviewable.

For this repo, squash merge is usually the better default because it keeps milestone history clean.

### Merge conditions

Before merging into `main`, confirm:

1. the branch scope is coherent;
2. the relevant validation has run;
3. the affected docs are updated;
4. no large raw datasets or temporary artefacts are included;
5. the change does not silently alter methodology.

### Self-review rule

Even when working alone, do a quick self-review before merge.

Check especially for:
- timeout changes
- flow-key drift
- packet-vs-byte labelling errors
- detection denominator mistakes
- stale module docs
- accidental large-file additions
- debug artefacts left in the repo

---

## Validation gates

### Minimum gate for any non-trivial change
Run at least one of:
- focused unit tests for the changed logic;
- one tiny local example;
- one end-to-end demo run for orchestration changes.

### Required gate by change type

#### Code logic changes
Run:
- relevant unit tests
- one small behavioural check where practical

#### Refactors with intended no semantic change
Run:
- existing tests covering the touched module
- at least one small regression check

#### Performance changes
Run:
- correctness checks first
- then the performance-oriented run or measurement
- document remaining risk if peak memory was inferred rather than directly measured

#### Orchestration, logging, output-path, or config changes
Run:
- one tiny end-to-end execution
- confirm outputs land in expected locations
- confirm manifests/logs are written as intended

#### Documentation-only changes
No code validation is required unless the docs describe behaviour that is no longer true.
In that case, validate the behaviour before merging the docs.

---

## Doc synchronisation rules

Update docs in the same branch when the change affects any of the following:
- architecture
- execution model
- output paths
- config schema
- module inputs or outputs
- assumptions
- test expectations
- workflow expectations

### Required doc mapping

#### Architecture changes
Update:
- `docs/hot/pipeline-v2.md`
- relevant module docs
- `AGENTS.md` only if repo-wide rules changed

#### Workflow changes
Update:
- `docs/hot/git-workflow.md`
- `AGENTS.md` only if the rule must be enforced repo-wide

#### Module behaviour changes
Update:
- `docs/modules/<module>/README.md`
- `docs/modules/<module>/CHANGELOG.md` when the change affects module purpose, architecture, direction, interface contracts, or milestone state
- `docs/modules/<module>/Maintenance.md` when maintenance guidance changed

Module-level `CHANGELOG.md` files are retained, but they should not be used as routine implementation diaries.

### Frozen-doc rule
Do not rewrite frozen architecture docs to match ongoing work.

Frozen docs should only receive:
- factual corrections
- compatibility notes
- pointers to newer active specs

---

## Codex-specific workflow

### Before a substantial Codex task
Checkpoint the repo first.

Use one of:
- a normal commit
- a temporary checkpoint commit
- a clean stash if the change truly should not enter history yet

Do not start large Codex-driven edits from a dirty, uncheckpointed state.

### During Codex work
Prefer task prompts that specify:
- scope
- constraints
- validation
- stop condition

Do not ask Codex for a repo-wide rewrite when only one slice is intended.

### After Codex completes a slice
Before merging:
- inspect the diff manually;
- check for methodology drift;
- run the promised validation;
- ensure docs moved with code.

### Codex branch rule
Use a dedicated working branch for substantial Codex work.
Do not let Codex make large changes directly on `main`.

---

## Tags and milestone naming

Use tags for architecture milestones.

Recommended tags:
- `pipeline-mvp-freeze`
- `pipeline-v2-freeze`

Or, if you prefer semver-style research milestones:
- `v0.1.0` for frozen MVP
- `v0.2.0` for the first validated post-MVP architecture

### Tagging rule
Create a tag only when:
- the architecture state is validated;
- the docs reflect that state;
- the milestone is worth referring back to later.

Do not tag every small branch merge.

---

## Release and milestone policy

Treat milestone freezes as documentation events as well as code events.

For a milestone freeze:
1. ensure `main` is clean;
2. ensure docs are in sync;
3. ensure the relevant tests or demo run pass;
4. create the milestone tag;
5. record the freeze in the active architecture doc and, if useful, a milestone note or release description.

---

## Large-file and artefact policy

Never commit these by accident:
- large raw packet captures
- large archives
- temporary extraction outputs
- cache directories
- local logs that are not intentional examples
- virtual environments
- IDE state

Before commit, check:
- `git status`
- `.gitignore` coverage
- whether generated outputs are truly meant to be versioned

Small reproducible fixtures, summaries, example plots, and compact result tables are acceptable when they support testing or documentation.

---

## Conflict resolution policy

When rebasing or merging, prioritise:
1. methodology correctness
2. code correctness
3. doc correctness
4. history neatness

If a conflict suggests two branches changed methodology differently, stop and resolve the methodology explicitly.
Do not auto-resolve and hope the tests catch it later.

---

## Emergency fixes

For a small urgent correction on `main`, such as:
- a broken command
- a config typo
- a documentation error blocking use
- a test failure caused by a recent merge

Use:
- `fix/<scope>`

Keep the branch narrow and merge it quickly after validation.

Do not bundle unrelated cleanup into emergency fixes.

---

## Recommended everyday workflow

1. sync `main`
2. create a scoped working branch
3. make one coherent change
4. validate it
5. update affected docs
6. self-review the diff
7. merge back into `main`
8. tag only if this was a true milestone

---

## Definition of a good branch

A branch is good when:
- its purpose is obvious from the name;
- its diff is reviewable;
- its validation story is honest;
- its docs are in sync;
- it can be merged without confusing future you.

That is more important than following a complicated formal branching model.
