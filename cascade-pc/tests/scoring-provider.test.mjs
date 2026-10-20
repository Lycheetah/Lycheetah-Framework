import assert from 'node:assert/strict'
import { copyFileSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import test from 'node:test'
import { pathToFileURL } from 'node:url'

// Load the actual browser ES modules without changing Electron's CommonJS entry.
const fixture = mkdtempSync(join(tmpdir(), 'lycheetah-scoring-test-'))
writeFileSync(join(fixture, 'package.json'), '{"type":"module"}')
for (const name of ['ai.js', 'frameworks.js']) {
  copyFileSync(new URL(`../src/scoring/${name}`, import.meta.url), join(fixture, name))
}
const { consensusScore } = await import(pathToFileURL(join(fixture, 'ai.js')).href)
test.after(() => rmSync(fixture, { recursive: true, force: true }))

for (const [fails, changes] of [[false, false], [true, false], [false, true]]) {
  test(`parallel scoring preserves provider choice; failure=${fails}, edit=${changes}`, async (t) => {
    const previousStorage = globalThis.localStorage
    const previousFetch = globalThis.fetch
    t.after(() => {
      if (previousStorage === undefined) delete globalThis.localStorage
      else globalThis.localStorage = previousStorage
      globalThis.fetch = previousFetch
    })
    const values = new Map([
      ['cascade_provider', 'openai'],
      ['cascade_deepseek_key', 'fixture-value'],
      ['cascade_openai_key', 'fixture-value'],
    ])
    globalThis.localStorage = {
      getItem: key => values.get(key) ?? null,
      setItem: (key, value) => values.set(key, String(value)),
    }
    const replies = new Map()
    const layers = JSON.stringify(Array.from({ length: 9 }, () => ({ framework_score: 50 })))
    globalThis.fetch = url => new Promise(resolve => {
      const provider = url.includes('deepseek') ? 'deepseek' : 'openai'
      replies.set(provider, () => resolve({
        ok: !(fails && provider === 'openai'),
        status: 503,
        text: async () => 'synthetic failure',
        json: async () => ({ choices: [{ message: { content: layers } }] }),
      }))
    })
    const pending = consensusScore('Fixture', 'Synthetic content', '')
    assert.deepEqual([...replies.keys()], ['deepseek', 'openai'])
    if (changes) values.set('cascade_provider', 'ollama')
    replies.get('deepseek')()
    await new Promise(resolve => setImmediate(resolve))
    replies.get('openai')()
    if (fails) await assert.rejects(pending, /Not enough providers/)
    else assert.equal((await pending).providers.length, 2)
    assert.equal(values.get('cascade_provider'), changes ? 'ollama' : 'openai')
  })
}
