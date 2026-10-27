import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';

const root = resolve('build/deepseek-package');
const plugin = await import(pathToFileURL(join(root, 'index.mjs')).href);
test('DSH registry contract and lifecycle return', () => {
  let registration;
  const dispose = () => {};
  const result = plugin.apply({ skills: { register(value) { registration = value; return dispose; } } });
  assert.equal(result, dispose);
  assert.equal(registration.name, 'boolean-vector-research');
  assert.deepEqual(plugin.inject, ['skills']);
  assert.equal(registration.invocation.modelInvocable, true);
  assert.equal(registration.resourceBase.kind, 'directory');
  assert.ok(existsSync(join(registration.resourceBase.path, 'resources/research_core.py')));
  assert.ok(registration.content.includes('能力路由'));
});
test('DSH carries identical frozen skill resources', () => {
  const dir=join(root,'skills/boolean-vector-research');
  const edition=JSON.parse(readFileSync(join(dir,'EDITION.json'),'utf8'));
  for (const [name,digest] of Object.entries(edition.files)) {
    assert.equal(createHash('sha256').update(readFileSync(join(dir,name))).digest('hex'),digest,name);
  }
});
test('DSH package exposes a local bundle patch', () => {
  const manifest=JSON.parse(readFileSync(join(root,'package.json'),'utf8'));
  assert.equal(manifest.version,'1.0.0');
  assert.equal(manifest.dsh.bundle.patch,'./cordis.patch.yml');
  assert.ok(readFileSync(join(root,'cordis.patch.yml'),'utf8').includes('dsh-boolean-vector-research'));
});
