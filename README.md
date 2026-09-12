# hermes-labs-ai/claude-plugins

Claude Code plugin marketplace for Hermes Labs. This repo holds only the
marketplace manifest (`.claude-plugin/marketplace.json`) — each plugin's code
stays in its own repo and is pulled in by Claude Code at install time.

## Install

```
claude plugin marketplace add hermes-labs-ai/claude-plugins
/plugin install <name>@hermes-labs
```

For example:

```
/plugin install little-canary@hermes-labs
/plugin install claude-trash-guard@hermes-labs
```

`claude plugin list` shows what's installed; `claude plugin marketplace update
hermes-labs` refreshes the manifest from `main`.

## Plugins

| Name | Version | What it does | Source repo |
|---|---|---|---|
| `hermes-blind` | 0.3.0 | Local recovery anchors for Claude Code and Codex sessions, plus evidence-gated evaluation prompts | [hermes-blind](https://github.com/hermes-labs-ai/hermes-blind) |
| `lintlang` | 0.1.1 | Returns concise LintLang repair guidance after Claude Code changes a supported language-bearing file | [lintlang](https://github.com/hermes-labs-ai/lintlang) (`integrations/claude-code`) |
| `rule-audit` | 0.1.0 | On-demand static analysis of AI system prompts — contradictions, coverage gaps, priority ambiguities, meta-paradoxes | [rule-audit](https://github.com/hermes-labs-ai/rule-audit) (`integrations/claude-code`) |
| `hermeneutic-gate` | 0.1.7 | Legacy advisory Stop-hook bundle for the fixed English gate. **Not certified against current Claude Stop behavior in v0.1.7** — prefer the CLI directly. Requires the `hermeneutic` package | [hermeneutic](https://github.com/hermes-labs-ai/hermeneutic) (`claude-plugin`) |
| `little-canary` | 0.3.6 | Blocks a Claude Code turn when a local Little Canary server rejects the submitted prompt | [little-canary](https://github.com/hermes-labs-ai/little-canary) (`plugins/claude-code`) |
| `claude-trash-guard` | 0.1.2 | Blocks permanent-delete shell commands and redirects to a recoverable trash workflow | [agent-trash-guard](https://github.com/hermes-labs-ai/agent-trash-guard) (`integrations/claude`) |

Not included: **agent-signage** was not available to verify against at prep
time — check whether it ships a `.claude-plugin/plugin.json` before adding it
here.

## Adding a plugin

1. The upstream repo needs a `.claude-plugin/plugin.json` (see any repo above
   for the shape: `name`, `version`, `description`, `author`, `homepage`,
   `repository`, `license`).
2. Add an entry to `plugins` in `.claude-plugin/marketplace.json`:
   ```json
   {
     "name": "<plugin name>",
     "description": "<one line>",
     "version": "<matches upstream plugin.json>",
     "category": "<development|developer-tools|security|...>",
     "source": {
       "source": "github",
       "repo": "hermes-labs-ai/<repo>",
       "path": "<subdir, omit if plugin.json is at repo root>",
       "ref": "main"
     }
   }
   ```
3. Validate before committing: `claude plugin validate .claude-plugin/marketplace.json --strict`
4. Bump `version` here whenever the upstream plugin bumps its own — this repo
   does not re-derive it automatically.

## Notes

- `source.ref` pins every plugin to its repo's `main` branch. Pin to a tag
  instead once any of these plugins starts cutting releases.
- This marketplace only serves Claude Code plugins. Several of these repos
  (`rule-audit`, `hermeneutic`, `agent-trash-guard`) also ship a Codex
  plugin under a separate `.codex-plugin/` — those are not part of this
  manifest.
