<div align="center">

# Fidelis for Loki

An opt-in [Loki](https://github.com/wundercorp/loki) memory provider backed by the local [Fidelis](https://github.com/hermes-labs-ai/fidelis) service.

Fidelis for Loki is developed by [Hermes Labs](https://hermes-labs.ai).

Hermes Labs is an agentic infrastructure company building the reliability layer for autonomous systems.

</div>

It uses Loki's `MemoryProvider` plugin API; no Loki core patch or MCP server registration is required.

## What it does

- Recalls up to five current local memories for a substantive user turn. Superseded, expired, and not-yet-valid records are excluded from automatic context.
- Offers `fidelis_recall` for explicit fast or zero-LLM hybrid search, including record IDs and temporal status.
- Offers `fidelis_store` for deliberate verbatim facts and `fidelis_correct` to replace an outdated record by ID. It never automatically archives the conversation.
- Reports queued writes as pending, never as stored or recallable.

Fidelis stays local. The adapter sends JSON only to `127.0.0.1` on `FIDELIS_PORT` (default `19420`), matching the Fidelis CLI. It uses Python's standard library and adds no plugin dependencies. Loki's built-in `MEMORY.md` and `USER.md` remain available.

## Install

1. Install and initialize [Fidelis Memory 0.3.0rc1 or newer](https://github.com/hermes-labs-ai/fidelis/releases/tag/v0.3.0rc1). That release provides the record lookup needed for safe corrections. Its service needs Ollama and `nomic-embed-text` for retrieval. Confirm `fidelis health` reports a ready local service before activating the plugin.
2. Install the plugin with `loki plugins install hermes-labs-ai/plugins/adapters/loki/fidelis` (or use a full plugins-repository commit SHA with `--ref` to pin it). Loki selects this subdirectory and installs the manifest name `fidelis`. Loki treats direct Git installs as custom plugins until a maintainer admits them to its catalog.
3. Run `loki memory setup` and select `fidelis`. The provider is per Loki profile; Fidelis itself uses the locally configured store. Restart a running Loki session to pick up the new provider.

If Fidelis uses a nondefault port, set `FIDELIS_PORT` for the Loki process to the same port. The plugin performs no network call during discovery; an unavailable service leaves automatic recall empty and makes explicit tools return an error. A port outside 1–65535 makes the provider unavailable.

## Validate

From a Loki checkout with its dependencies installed, using a checkout of this repository:

```sh
loki plugins validate /path/to/plugins/adapters/loki/fidelis
PYTHONPATH=/path/to/loki python -m unittest discover -s /path/to/plugins/adapters/loki/fidelis/tests -v
```

The integration tests exercise real Loki provider discovery and `MemoryManager` against a loopback Fidelis wire stub. No user memory is read or written by the tests.

## Migration from the standalone repository

This directory is the maintained source. The standalone `loki-fidelis` repository has been retired. Existing installed copies can still run; switch their update source to this directory with `loki plugins install hermes-labs-ai/plugins/adapters/loki/fidelis --force`. If the old source was pinned, also pass `--ref <full-plugins-commit-SHA>`; Loki requires an explicit revision when replacing a pinned installation.

The adapter retains its original [MIT license](LICENSE). Fidelis itself remains independently packaged as `fidelis-memory`.

## Compatibility

The plugin targets Loki's documented external memory provider API on current `main`. It uses Fidelis's `/query`, `/recall_hybrid`, `/get`, and `/store` local HTTP contracts in 0.3.0rc1. Fidelis 0.2.0 can serve recall and storage, but lacks `/get`; correction returns an upgrade hint on that release. The plugin is maintained by Hermes Labs, independently of Loki's core release cycle.
