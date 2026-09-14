// Regression coverage for the catalog manifest.
//
// Guards the failure this repo actually hit: a cross-repo entry written as
// {"source":"github","repo":...}. Claude Code resolves that form over
// git@github.com with no HTTPS fallback, so on any machine without an SSH key
// for the org the install aborts and no plugin lands. Every entry here must
// use the git-subdir form with an explicit HTTPS url.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const manifestPath = fileURLToPath(
  new URL('../.claude-plugin/marketplace.json', import.meta.url),
);
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));

const SSH_URL = /^(git@|ssh:\/\/|git:\/\/)/;

test('manifest declares plugins', () => {
  assert.ok(Array.isArray(manifest.plugins));
  assert.ok(manifest.plugins.length > 0);
});

for (const plugin of manifest.plugins) {
  test(`${plugin.name}: source is git-subdir, not a repo root source`, () => {
    assert.equal(
      plugin.source.source,
      'git-subdir',
      `"${plugin.source.source}" resolves over SSH; use git-subdir with an HTTPS url`,
    );
    assert.ok(
      !('repo' in plugin.source),
      'a bare "repo" key is the root-source form that clones over SSH',
    );
  });

  test(`${plugin.name}: url is HTTPS and the entry is fully pinned`, () => {
    const { url, path, ref } = plugin.source;
    assert.ok(!SSH_URL.test(url), `${url} is an SSH url`);
    assert.match(url, /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\.git$/);
    assert.ok(typeof path === 'string' && path.length > 0);
    assert.ok(typeof ref === 'string' && ref.length > 0);
  });
}

test('hermes-blind points at the cross-repo package', () => {
  const entry = manifest.plugins.find((p) => p.name === 'hermes-blind');
  assert.ok(entry, 'hermes-blind is missing from the catalog');
  assert.deepEqual(entry.source, {
    source: 'git-subdir',
    url: 'https://github.com/hermes-labs-ai/hermes-blind.git',
    path: 'claude-plugin',
    ref: 'main',
  });
  assert.equal(entry.version, '0.3.0');
});
