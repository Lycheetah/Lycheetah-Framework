import assert from 'node:assert/strict'
import http from 'node:http'
import { createRequire } from 'node:module'
import test from 'node:test'

const { createApiHandler } = createRequire(import.meta.url)('../local-api.js')

const db = {
  pyramids: [{ id: 'p1', name: 'Fixture pyramid' }],
  files: [], blocks: [{ id: 'b1', title: 'Private note', content: 'synthetic' }],
  onion_layers: [], audit_log: [],
}
const server = http.createServer(createApiHandler(() => db))
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve))
const { port } = server.address()
test.after(() => server.close())

function get(path, headers = {}, method = 'GET') {
  return new Promise((resolve, reject) => {
    const req = http.request({ host: '127.0.0.1', port, path, method, headers }, res => {
      let body = ''
      res.on('data', chunk => { body += chunk })
      res.on('end', () => resolve({ status: res.statusCode, body: JSON.parse(body) }))
    })
    req.on('error', reject)
    req.end()
  })
}

test('a script on this machine can read the API', async () => {
  for (const host of ['127.0.0.1:7432', 'localhost:7432']) {
    const res = await get('/pyramids', { host })
    assert.equal(res.status, 200)
    assert.equal(res.body[0].name, 'Fixture pyramid')
  }
  assert.equal((await get('/status', { host: 'localhost:7432', origin: 'http://localhost:5173' })).status, 200)
})

test('a rebound hostname cannot read the database', async () => {
  const res = await get('/blocks', { host: 'attacker.example:7432' })
  assert.equal(res.status, 403)
  assert.ok(!JSON.stringify(res.body).includes('Private note'))
})

test('a foreign web origin is refused even with a local Host', async () => {
  assert.equal((await get('/blocks', { host: '127.0.0.1:7432', origin: 'https://attacker.example' })).status, 403)
  assert.equal((await get('/blocks', { host: '127.0.0.1:7432', origin: 'null' })).status, 403)
})

test('the API stays read-only', async () => {
  assert.equal((await get('/pyramids', { host: '127.0.0.1:7432' }, 'POST')).status, 405)
})
