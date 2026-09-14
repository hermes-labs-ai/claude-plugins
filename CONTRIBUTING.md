# Contributing to claude-plugins

Thank you for your interest in this marketplace. This repo carries only the
manifest (`.claude-plugin/marketplace.json`) that lets Claude Code find and
install Hermes Labs plugins — it does not carry any plugin's code, so
"contributing a plugin" means listing an existing, working plugin here, not
building one in this repo.

## What belongs in this marketplace

- The plugin has its own repository (or its own subdirectory of a repository)
  with a `.claude-plugin/plugin.json` at the appropriate path, and that
  `plugin.json` already declares `name`, `version`, `description`, `author`,
  `homepage`, `repository`, and `license`.
- The plugin is a Claude Code plugin specifically — a hook, command, or
  on-demand script Claude Code can install and run. A Codex or Gemini
  extension living in the same source repo is not itself listed here.
- The plugin does what its description says. If it can't verify something
  (a runtime behavior, a certification, a compatibility claim), its README
  says so instead of implying it.

## Reporting a problem with a listed plugin

- Search [existing issues](https://github.com/hermes-labs-ai/claude-plugins/issues)
  first to avoid duplicates.
- Open an issue naming the affected plugin, the manifest entry you expected,
  and what actually happened (install failure, wrong version, broken
  `source`, stale description).
- For a bug in the plugin's own behavior, file it in that plugin's own repo
  instead — this repo only tracks the manifest entry, not the plugin's code.

## Proposing a plugin

1. Fork the repository.
2. Create a feature branch from `main` (`git checkout -b add-my-plugin`).
3. Add one entry to `plugins` in `.claude-plugin/marketplace.json`. The
   README's "Adding a plugin" section has the exact JSON shape for both
   supported `source` types (`github` for a plugin at the repo root,
   `git-subdir` for one in a subdirectory) — follow it precisely; an
   unsupported `source` shape passes the schema but fails at install time.
4. Validate before opening the pull request:
   ```bash
   claude plugin validate .claude-plugin/marketplace.json --strict
   ```
   Then actually install it locally — `claude plugin marketplace add .`
   followed by `claude plugin install <name>@hermes-labs` — since the
   validator does not catch an unsupported `source` shape on its own.
5. Open a pull request against `main` describing the plugin in one line,
   linking its source repo, and confirming the local install step above
   actually worked.
6. Keep the version in the manifest entry in sync with the upstream plugin's
   own `.claude-plugin/plugin.json` going forward — this repo does not
   re-derive it automatically.

## Scope

This marketplace only serves plugins that Hermes Labs itself builds and
maintains. It is not a general Claude Code plugin registry, and it does not
accept third-party plugins unrelated to Hermes Labs' own tools.

## Questions?

Open an issue or start a discussion on the repository.
