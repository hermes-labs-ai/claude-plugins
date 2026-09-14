// Regression coverage for the catalog manifest.
//
// Guards the failure this repo actually hit: a cross-repo entry written as
// {"source":"github","repo":...}. Claude Code resolves that form over
// git@github.com with no HTTPS fallback, so on any machine without an SSH key
// for the org the install aborts and no plugin lands. Every entry here must
// use an explicit HTTPS git source. Use git-subdir for subdirectories and url
// for repo-root plugins whose nested components must all be included.

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
  test(`${plugin.name}: source avoids an SSH-based root source`, () => {
    assert.ok(
      ['git-subdir', 'url'].includes(plugin.source.source),
      `"${plugin.source.source}" is not an accepted HTTPS git source`,
    );
    assert.ok(
      !('repo' in plugin.source),
      'a bare "repo" key is the root-source form that clones over SSH',
    );
  });

  test(`${plugin.name}: url is HTTPS and the entry is fully pinned`, () => {
    const { url, ref } = plugin.source;
    assert.ok(!SSH_URL.test(url), `${url} is an SSH url`);
    assert.match(url, /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\.git$/);
    assert.ok(typeof ref === 'string' && ref.length > 0);
    if (plugin.source.source === 'git-subdir') {
      assert.ok(
        typeof plugin.source.path === 'string' && plugin.source.path.length > 0,
      );
    } else {
      assert.equal(plugin.source.source, 'url');
      assert.ok(!('path' in plugin.source));
    }
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

test('agent-kickstart uses a full HTTPS git source for its repo-root plugin', () => {
  const entry = manifest.plugins.find((p) => p.name === 'agent-kickstart');
  assert.ok(entry, 'agent-kickstart is missing from the catalog');
  assert.deepEqual(entry.source, {
    source: 'url',
    url: 'https://github.com/hermes-labs-ai/agent-kickstart.git',
    ref: 'main',
  });
  assert.equal(entry.version, '0.3.0');
});
