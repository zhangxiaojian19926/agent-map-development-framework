const test = require('node:test')
const assert = require('node:assert/strict')
const { assertSummary } = require('../src/schema')
const { FlakyLlmProvider, buildLlmFromEnv, MockLlmProvider } = require('../src/llm')
const { fail } = require('../src/errors')
const { withApp, login, consented, api, waitJob, CHAT } = require('./helpers')

test('chunking plus merge returns the fixed summary schema', async function () {
  await withApp({ chunkCharBudget: 220 }, async function (app, base) {
    const token = await login(base)
    const lines = []
    for (let i = 0; i < 24; i++) {
      const minute = String(i).padStart(2, '0')
      lines.push('2026-01-02 10:' + minute + ':00 张三: 这是第' + i + '条比较长的讨论，请确认纪要已经记下。')
    }
    lines.push('2026-01-02 11:00:00 李四: 就这么定了？')
    lines.push('2026-01-02 11:01:00 张三: 好，就这么定，周五前交。')
    const created = await api(base, token, 'POST', '/api/jobs', consented({
      source: 'paste',
      text: lines.join('\n')
    }))
    const job = await waitJob(base, token, created.json.id)
    assert.equal(job.status, 'done')
    assert.equal(job.chunkCount >= 3, true)
    const summary = assertSummary(job.result)
    assert.equal(summary.participants.includes('张三'), true)
    assert.equal(summary.participants.includes('李四'), true)
    assert.equal(summary.key_points.length > 0, true)
    assert.equal(summary.action_items.length > 0, true)
    assert.equal(summary.decisions.some(function (item) { return item.includes('就这么定') }), true)
    assert.equal(summary.open_questions.some(function (item) { return item.includes('？') }), true)
    assert.equal(summary.action_items[0].due === null || typeof summary.action_items[0].due === 'string', true)
    const chunkCalls = app.llm.calls.filter(function (call) { return call.op === 'chunk' })
    const mergeCalls = app.llm.calls.filter(function (call) { return call.op === 'merge' })
    assert.equal(chunkCalls.length, job.chunkCount)
    assert.equal(mergeCalls.length, 1)
  })
})

test('a single short chat still matches the schema and retries a transient LLM failure', async function () {
  const flaky = new FlakyLlmProvider({ failuresLeft: 1 })
  await withApp({ llm: flaky }, async function (app, base) {
    const token = await login(base)
    const created = await api(base, token, 'POST', '/api/jobs', consented({ source: 'paste', text: CHAT }))
    const job = await waitJob(base, token, created.json.id)
    assert.equal(job.status, 'done')
    assert.equal(job.result.title.includes('张三'), true)
    assert.equal(job.result.action_items.some(function (item) { return item.due === '周五前' }), true)
    assert.equal(flaky.calls.filter(function (call) { return call.op === 'chunk' }).length >= 2, true)
  })
})

test('schema violations fail the job instead of returning a partial object', async function () {
  const bad = {
    calls: [],
    async summarizeChunk() {
      this.calls.push('chunk')
      throw fail(502, 'SCHEMA_INVALID', '摘要缺少 title')
    },
    async mergeSummaries() {
      return { title: '' }
    }
  }
  await withApp({ llm: bad }, async function (app, base) {
    const token = await login(base)
    const created = await api(base, token, 'POST', '/api/jobs', consented({ source: 'paste', text: CHAT }))
    const job = await waitJob(base, token, created.json.id)
    assert.equal(job.status, 'failed')
    assert.equal(job.error.code, 'SCHEMA_INVALID')
    assert.equal(job.result, null)
  })
})

test('default provider is the mock unless openai credentials are set', function () {
  assert.equal(buildLlmFromEnv({}) instanceof MockLlmProvider, true)
  assert.equal(buildLlmFromEnv({ LLM_PROVIDER: 'minimax' }) instanceof MockLlmProvider, true)
  const real = buildLlmFromEnv({ LLM_PROVIDER: 'openai', LLM_API_KEY: 'test-key', LLM_MODEL: 'demo' })
  assert.equal(real.constructor.name, 'OpenAICompatibleProvider')
  assert.equal(real.model, 'demo')
  const minimax = buildLlmFromEnv({
    LLM_PROVIDER: 'minimax',
    MINIMAX_API_KEY: 'test-key',
    DEEPSEEK_API_KEY: 'unused'
  })
  assert.equal(minimax.constructor.name, 'OpenAICompatibleProvider')
  assert.equal(minimax.model, 'MiniMax-M3.1-Flash')
  assert.equal(minimax.baseUrl, 'https://api.minimax.cn/v1')
  assert.equal(minimax.apiKey, 'test-key')
})
