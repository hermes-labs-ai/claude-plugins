# hermes-labs-ai/claude-plugins

[![validate-marketplace](https://github.com/hermes-labs-ai/claude-plugins/actions/workflows/validate-marketplace.yml/badge.svg)](https://github.com/hermes-labs-ai/claude-plugins/actions/workflows/validate-marketplace.yml)

Claude Code plugin marketplace for Hermes Labs. This repo holds only the
marketplace manifest (`.claude-plugin/marketplace.json`) — each plugin's code
stays in its own repo and is pulled in by Claude Code at install time.

## Add the marketplace

```
/plugin marketplace add hermes-labs-ai/claude-plugins
```

Then install what you need:

```
/plugin install little-canary@hermes-labs
/plugin install claude-trash-guard@hermes-labs
```

`claude plugin list` shows what's installed; `/plugin marketplace update
hermes-labs` refreshes the manifest from `main`.

## Plugins

| Name | Version | What it does | Source repo |
|---|---|---|---|
| `hermes-blind` | 0.2.0 | Local recovery anchors for a Claude Code or Codex session, plus evidence-gated evaluation prompts — for picking a session back up without trusting its own self-report | [hermes-blind](https://github.com/hermes-labs-ai/hermes-blind) (`claude-plugin`) |
| `lintlang` | 0.1.1 | Runs LintLang after Claude Code edits a supported prompt/config file and returns concise repair guidance for what it finds | [lintlang](https://github.com/hermes-labs-ai/lintlang) (`integrations/claude-code`) |
| `rule-audit` | 0.1.0 | On-demand static analysis of an AI system prompt or AGENTS.md: contradictions, coverage gaps, priority ambiguities, meta-paradoxes | [rule-audit](https://github.com/hermes-labs-ai/rule-audit) (`integrations/claude-code`) |
| `hermeneutic-gate` | 0.1.7 | Legacy advisory Stop-hook bundle for the fixed English gate. **Not certified against current Claude Stop behavior in v0.1.7** — prefer the `hermeneutic` CLI directly | [hermeneutic](https://github.com/hermes-labs-ai/hermeneutic) (`claude-plugin`) |
| `little-canary` | 0.3.6 | Blocks a Claude Code turn when a local Little Canary server rejects the submitted prompt | [little-canary](https://github.com/hermes-labs-ai/little-canary) (`plugins/claude-code`) |
| `claude-trash-guard` | 0.1.2 | Blocks permanent-delete shell commands (`rm -rf` and friends) and redirects the agent to a recoverable trash workflow instead | [agent-trash-guard](https://github.com/hermes-labs-ai/agent-trash-guard) (`integrations/claude`) |
| `agent-signage` | 0.1.2 | A `PreToolUse` hook that reports when the file you're about to touch sits in a git checkout that's behind its upstream — stays silent otherwise | [agent-signage](https://github.com/hermes-labs-ai/agent-signage) (`claude-plugin`) |

## What these have in common

None of these are a framework you adopt. Each one is a small, deterministic
check — a hook or an on-demand script — aimed at one specific, verifiable
failure mode we've hit running agentic coding sessions ourselves: a destructive
shell command, a stale checkout, an unreviewed prompt, a contradiction buried
in a system prompt, a session that's lost its anchors. Where a check can be
done without an LLM call, it is; where a plugin can't verify something (see
`hermeneutic-gate` above), the README says so instead of claiming it.

## Adding a plugin

1. The upstream repo needs a `.claude-plugin/plugin.json` (see any repo above
   for the shape: `name`, `version`, `description`, `author`, `homepage`,
   `repository`, `license`).
2. Add an entry to `plugins` in `.claude-plugin/marketplace.json`. If
   `plugin.json` lives at the repo root, use the `github` source:
   ```json
   {
     "name": "<plugin name>",
     "description": "<one line>",
     "version": "<matches upstream plugin.json>",
     "category": "<development|developer-tools|security|...>",
     "source": {
       "source": "github",
       "repo": "hermes-labs-ai/<repo>",
       "ref": "main"
     }
   }
   ```
   If the plugin lives in a subdirectory of the repo (every plugin above
   except `hermes-blind`), `github` + a `path` field is **not** a valid
   source — use `git-subdir` instead, which sparsely clones just that
   subdirectory:
   ```json
   {
     "name": "<plugin name>",
     "description": "<one line>",
     "version": "<matches upstream plugin.json>",
     "category": "<development|developer-tools|security|...>",
     "source": {
       "source": "git-subdir",
       "url": "https://github.com/hermes-labs-ai/<repo>.git",
       "path": "<subdir containing .claude-plugin/plugin.json>",
       "ref": "main"
     }
   }
   ```
3. Validate before committing: `claude plugin validate .claude-plugin/marketplace.json --strict`
   — then actually install it locally (`claude plugin marketplace add .`
   plus `claude plugin install <name>@hermes-labs`) before pushing, since the
   validator does not catch an unsupported `source` shape.
4. Bump `version` here whenever the upstream plugin's own `.claude-plugin/plugin.json`
   bumps its version — this repo does not re-derive it automatically, and a
   repo's overall package version (pyproject.toml/package.json) can move
   independently of its Claude Code plugin's own version.

## Notes

- `source.ref` pins every plugin to its repo's `main` branch. Pin to a tag
  instead once any of these plugins starts cutting releases.
- This marketplace only serves Claude Code plugins. Several of these repos
  (`rule-audit`, `hermeneutic`, `agent-trash-guard`, `agent-signage`) also
  ship a Codex or Gemini extension elsewhere in the same repo — those are
  not part of this manifest.
