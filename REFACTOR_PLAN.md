## KittnTabbR-AI Refactor Plan

### Objectives

1. Normalize every user-facing product name, service identifier, and doc reference to `KittnTabbR-AI`.
2. Introduce a centralized AI harness that can mediate decisions across the application.
3. Preserve the existing cross-platform file-watching behavior with deterministic fallbacks.
4. Keep infrastructure concerns isolated enough that the project can still be maintained.

### Architecture Direction

The repo already has useful boundaries: watcher orchestration, metadata inference, movers, launchers, config, and secrets. The refactor keeps those boundaries, but routes prompt-backed decision making through a shared infrastructure adapter, `recursive_harness.py`, instead of embedding ad hoc Anthropic calls throughout the code.

This keeps the project closer to a lightweight hexagonal shape:

- `watcher.py` remains the entrypoint and orchestration layer.
- `metadata.py` remains the tab inference use case.
- `movers/` and `launchers/` remain infrastructure adapters for filesystem and OS startup integration.
- `recursive_harness.py` becomes the single LLM gateway.
- `branding.py` becomes the single source of truth for product identity.

### Phases

1. Branding pass
   Rename docs, service names, logger names, launchd/systemd/task identifiers, and generated filenames.

2. Harness extraction
   Introduce a reusable prompt adapter with `ask_text()` and `ask_bool()` plus stable fallbacks.

3. Behavior rewiring
   Route metadata inference, helper formatting, platform selection, and selected runtime decisions through the harness.

4. Test realignment
   Mock the harness boundary in unit tests and update assertions for the new product identifiers.

5. Optional second wave
   If the repo wants to go deeper into the joke, split prompt intent definitions into dedicated domain use cases, or add a local fake model adapter for offline troll mode.

### Constraints

- Avoid hard-breaking the watcher, mover, and launcher flows.
- Keep the app functional even when the API is unavailable.
- Avoid scattering branding strings or raw Anthropic calls after the refactor.
- Preserve a path back to saner architecture if the joke stops being funny.
