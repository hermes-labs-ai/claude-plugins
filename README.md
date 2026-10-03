# hermes-labs-ai/plugins

[![validate-catalog](https://github.com/hermes-labs-ai/plugins/actions/workflows/validate-marketplace.yml/badge.svg)](https://github.com/hermes-labs-ai/plugins/actions/workflows/validate-marketplace.yml)

Canonical distribution catalog for Hermes Labs agent plugins. Product
implementations, MCP servers, skills, hooks, and release workflows remain in
their product repositories. This repository owns:

- `catalog.json`, the single reviewed build input;
- `scripts/generate.mjs`, which deterministically emits native host manifests;
- `scripts/verify.mjs`, which checks identifiers, host claims, immutable pins,
  generated output, and optionally the pinned upstream manifests.
- `adapters/<host>/<plugin>/`, small native adapters for hosts whose APIs need
  a bridge to an existing product. `catalog.json` records these separately as
  `nativeAdapters`; they are installed with the host's own installer.

## Generated manifests

| Host | Manifest | Marketplace name |
|---|---|---|
| Claude Code | `.claude-plugin/marketplace.json` | `hermes-labs` |
| Codex | `.agents/plugins/marketplace.json` | `hermes-labs` |
| GitHub Copilot CLI | `.github/plugin/marketplace.json` | `hermes-labs-copilot` |

The names are intentionally stable. Existing installs keep their current
plugin namespace while the repository moves from `claude-plugins` to
`plugins`. GitHub redirects the former repository URL after the rename.

## Install

Claude Code:

```text
/plugin marketplace add hermes-labs-ai/plugins
/plugin install hermes-blind@hermes-labs
```

Codex:

```bash
codex plugin marketplace add hermes-labs-ai/plugins
codex plugin add hermes-blind@hermes-labs
```

Hermes Gate is available through this marketplace as a listed, unverified
Codex plugin. Its marketplace entry installs the pinned portable bundle; it
does not certify that Codex loads or executes its hooks. The separate
`pip install hermes-gate` followed by `hermes-gate install-codex` route configures
Codex hooks directly. Choose one route per Codex home: installing both can
register the same behavior twice.

GitHub Copilot CLI:

```bash
copilot plugin marketplace add hermes-labs-ai/plugins
copilot plugin install hermes-blind@hermes-labs-copilot
```

`hermes-labs-ai/plugins` is the canonical Copilot route. The redundant
`copilot-plugins` repository has been retired; the marketplace name remains
`hermes-labs-copilot`.

### Migrating an existing Copilot marketplace

Run `copilot plugin list` and record the plugins installed from
`hermes-labs-copilot`. Uninstall those entries with
`copilot plugin uninstall PLUGIN@hermes-labs-copilot`, then switch the source:

```bash
copilot plugin marketplace remove hermes-labs-copilot
copilot plugin marketplace add hermes-labs-ai/plugins
```

Reinstall the recorded plugins using `copilot plugin install
PLUGIN@hermes-labs-copilot`. Replace the historical `claude-trash-guard` name
with `agent-trash-guard`, which supplies the native Copilot hook. LintLang and
Agent Signage also resolve to native Copilot packages in this catalog. Every
product in the former feed remains available; this catalog additionally lists
Hermes Rubric and newer plugin revisions.

GitHub documents the [marketplace registration and removal commands](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing).

## Antigravity

Use the Hermes tools you already have in Gemini CLI with Google's native
`agy plugin import gemini` route, or install an existing portable skill package.
See the [Antigravity guide](docs/antigravity.md) to choose a tool and bring across
its skills or MCP connection. Hook-based guardrails require a host-specific
adapter; the guide identifies those separately.

## Native host adapters

One catalog can distribute plugins across hosts, but their runtime APIs differ.
Use the existing MCP connection for shared tool access wherever a host supports
MCP. Features such as prompt-time recall or event hooks may need a small native
adapter. Keep that bridge here, while the product's service and logic stay in
the product repository. This avoids a separate repository per integration and
keeps product repositories free of host packaging.

The reusable layout is `adapters/<host>/<plugin>/`, containing the host's native
manifest, adapter, README, license, and integration tests. Add a `nativeAdapters`
row to `catalog.json` for discovery. These rows are independent of marketplace
entries and do not claim compatibility with other hosts. Validate with the
host's native validator and test against its real API before publishing.

### Loki

[Fidelis for Loki](adapters/loki/fidelis/) connects Loki's `MemoryProvider` API
to the existing local Fidelis HTTP service. It adds no plugin dependencies.

```bash
loki plugins install hermes-labs-ai/plugins/adapters/loki/fidelis
loki memory setup
```

Select `fidelis` in setup, then restart Loki. Add `--ref <full-plugins-commit-SHA>`
to the install command for an immutable pin. This is Loki's native subdirectory
install route; it remains a custom source rather than an entry in Loki's curated
catalog. Other tools can use the same adapter layout with their own host API.

## Capability language

The catalog records capability type and compatibility separately:

- `skill` means an on-demand workflow is available to a host.
- `mcp` means an MCP server connection is packaged.
- `hook` means a host event interceptor exists.
- `verified` means the capability has host-specific evidence. For Claude that
  evidence is a pilot-proof receipt for the exact pinned commit, enforced by
  `verify`. For Codex it rests on earlier manual checks, because no receipt can
  exist yet; see Runtime certification below.
- `listed-unverified` preserves an existing install route without claiming a
  completed runtime certification.
- `unsupported` keeps the entry out of that host manifest.

When a product needs different native package roots on different hosts, the
catalog can use separate rows with the same plugin ID and disjoint targets.
LintLang keeps the `lintlang` install name while Claude Code and Copilot CLI
resolve to their respective integration directories; no product files are
copied into this catalog.

Agent Trash Guard keeps the existing `claude-trash-guard` Claude install name.
Copilot CLI installs `agent-trash-guard@hermes-labs-copilot` from the product
repository's root Agent Plugins bundle, which includes its native Copilot hook
and recoverable-deletion skill. The Claude hook is not used as a Copilot hook.

Agent Signage also keeps one install name across hosts. Copilot CLI resolves
`agent-signage` to its native post-tool hook package, which adds context after
supported file operations; Claude Code keeps its existing pre-tool bundle.

A loaded skill does not prove that an MCP server connected. A connected MCP
server does not prove that a hook intercepted an event. An input-screening
hook does not block arbitrary output tool execution.

## Runtime certification

`verify.mjs` checks identifiers, pins and generated output, none of which can
tell you what a host actually loads. The pilot proof pack supplies that half:

```bash
node scripts/pilot-proof.mjs --host claude
```

For every entry targeting the host it adds the pushed marketplace branch over
public HTTPS, verifies the cloned marketplace HEAD is the exact commit being
certified, installs the entry, reads back the component inventory the host
loaded, compares it against the declared capabilities, uninstalls, and finally
restores the marketplace and plugin list
to their pre-run state. Certification refuses to start if the `hermes-labs`
marketplace or any target plugin is already present, and it refuses to replace
the canonical receipt unless the full run passes with successful state reads,
no unresolved checks, and verified restoration. The receipt records each host
command with its exit status, so a run that failed to clean up is visible
rather than silent.

`verify` then refuses any entry marked `verified` for a **certifiable** host
unless the committed receipt has a passing result for the same commit and
version. Bumping a pin without re-certifying fails; downgrading the entry to
`listed-unverified` is the other legitimate way to clear it. The check reads
the committed receipt, so it still runs in CI, where no agent host CLI is
installed.

Claude is currently the only certifiable host, and this is the honest state of
the other two:

| Host | Certifiable | What `verified` rests on today |
|---|---|---|
| Claude Code | yes | `evidence/pilot-proof-claude.json`, enforced by `verify` |
| Codex | no | earlier manual checks, not receipt-backed and not gated |
| GitHub Copilot CLI | no | direct CLI plugin and skill readback for verified skill entries; the pilot-proof pack does not yet automate this |

Codex and Copilot install the same pinned sources, but neither host has the
complete component inventory readback required by `pilot-proof.mjs`. Copilot's
`skill list` can verify an installed skill, but it does not certify a hook.
The pilot-proof pack refuses those hosts rather than imply evidence for every
declared capability. The five Codex
`verified` entries predate this pack; they are not downgraded here because that
would assert a negative the pack cannot demonstrate either. Extending coverage
means adding a host to `CERTIFIED_HOSTS` once a readback exists.

Two further limits are deliberate. `claude plugin details` reports slash
commands inside its `Skills` bucket, so `skill` and `command` are separated
from the installed plugin tree rather than from the inventory. And the pack
probes only `skill`, `mcp`, `hook` and `command`; an entry declaring a
schema-legal capability with no probe, such as `agent` or `lsp`, is failed
rather than passed by omission.

## Build and verify

Node.js 20 or newer is sufficient; there are no package dependencies.

```bash
npm run generate
npm test
npm run verify
npm run verify:network
claude plugin validate .claude-plugin/marketplace.json --strict
```

`verify:network` fetches every upstream plugin manifest at the exact 40-byte
commit recorded in `catalog.json` and checks its name and version. The normal
verifier is offline and fails if generated files drift from the catalog.

## Adding or updating an entry

1. Complete and review the product change in its product repository.
2. Record the immutable commit, released version, plugin root, capabilities,
   and host-specific compatibility in `catalog.json`.
3. Run `npm run generate`.
4. Commit and push the catalog plus generated marketplace manifests, then
   re-run `node scripts/pilot-proof.mjs --host claude` when the entry claims a
   `verified` host. The runner adds the pushed branch and refuses certification
   unless Claude's local marketplace clone resolves to that exact commit.
5. Run the checks above.
6. Commit `catalog.json`, all three generated manifests, and any updated
   receipt together.

Keep native adapters limited to host translation; do not copy product services
or core implementations into this repository. Never replace a commit pin
with a moving branch-only reference, or mark a host `verified` based only on
manifest parsing.
