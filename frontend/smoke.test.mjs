import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'

test('router includes phase 1 MVP routes', async () => {
  const routerSource = await readFile(new URL('./src/app/router.tsx', import.meta.url), 'utf8')
  for (const route of ['dashboard', 'ask-ai', 'portfolio-lab', 'learn', 'profile']) {
    assert.equal(routerSource.includes(`'${route}'`), true)
  }
})

test('frontend index title references The Better Investor', async () => {
  const html = await readFile(new URL('./index.html', import.meta.url), 'utf8')
  assert.equal(html.includes('<title>The Better Investor</title>'), true)
})
