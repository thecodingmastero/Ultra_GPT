import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'

test('router includes phase 1 MVP routes', async () => {
  const routerSource = await readFile(new URL('./src/app/router.tsx', import.meta.url), 'utf8')
  for (const route of ['dashboard', 'ask-ai', 'portfolio-lab', 'learn', 'profile', 'market', 'login', 'register']) {
    assert.equal(routerSource.includes(`'${route}'`), true)
  }
})

test('frontend index title references The Better Investor', async () => {
  const html = await readFile(new URL('./index.html', import.meta.url), 'utf8')
  assert.equal(html.includes('<title>The Better Investor</title>'), true)
})

test('auth pages are wired to backend endpoints', async () => {
  const loginSource = await readFile(new URL('./src/pages/LoginPage.tsx', import.meta.url), 'utf8')
  const registerSource = await readFile(new URL('./src/pages/RegisterPage.tsx', import.meta.url), 'utf8')
  assert.equal(loginSource.includes('/api/auth/login'), true)
  assert.equal(registerSource.includes('/api/auth/register'), true)
})

test('portfolio page uses holdings CRUD and concentration endpoint', async () => {
  const portfolioSource = await readFile(new URL('./src/pages/PortfolioPage.tsx', import.meta.url), 'utf8')
  for (const endpoint of ['/api/holdings', '/api/portfolio/concentration']) {
    assert.equal(portfolioSource.includes(endpoint), true)
  }
})

test('lessons page includes authenticated progress tracking', async () => {
  const learnSource = await readFile(new URL('./src/pages/LearnPage.tsx', import.meta.url), 'utf8')
  assert.equal(learnSource.includes('/api/lessons/progress'), true)
  assert.equal(learnSource.includes('Mark complete'), true)
})
