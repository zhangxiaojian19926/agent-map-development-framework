const test = require('node:test')
const assert = require('node:assert/strict')
const { LocalKeywordSafety, WeChatMsgSecCheck, ContentSafetyPipeline } = require('../src/safety')
const { withApp, login, consented, api, waitJob, CHAT } = require('./helpers')

test('local checker blocks a real rule and allows ordinary chat, including a split bypass', async function () {
  const checker = new LocalKeywordSafety()
  const blocked = await checker.check('转发：儿童色情链接')
  assert.equal(blocked.ok, false)
  assert.equal(blocked.ruleId, 'minor_sexual')
  assert.equal(blocked.provider, 'local-keyword')
  const split = await checker.check('儿 童 色 情')
  assert.equal(split.ok, false)
  const ordinary = await checker.check('儿童节我们决定办活动，谁负责场地？')
  assert.equal(ordinary.ok, true)
})

test('blocked chat never reaches the LLM; a nearby innocent chat does', async function () {
  await withApp({}, async function (app, base) {
    const token = await login(base)
    const ok = await api(base, token, 'POST', '/api/jobs', consented({ source: 'paste', text: CHAT }))
    const done = await waitJob(base, token, ok.json.id)
    assert.equal(done.status, 'done')
    const calls = app.llm.calls.length
    assert.equal(calls > 0, true)

    const bad = await api(base, token, 'POST', '/api/jobs', consented({
      source: 'paste',
      text: '2026-01-02 09:30:00 张三: 这里有儿童色情链接'
    }))
    const failed = await waitJob(base, token, bad.json.id)
    assert.equal(failed.status, 'failed')
    assert.equal(failed.error.code, 'CONTENT_BLOCKED')
    assert.equal(failed.error.ruleId, 'minor_sexual')
    assert.equal(app.llm.calls.length, calls)
  })
})

test('msgSecCheck adapter plugs in behind the local checker and is not called when local already blocks', async function () {
  let called = 0
  const wechat = new WeChatMsgSecCheck({
    getAccessToken: async function () { return 'token-1' },
    fetchImpl: async function (url, init) {
      called += 1
      assert.match(url, /\/wxa\/msg_sec_check\?access_token=/)
      const body = JSON.parse(init.body)
      assert.equal(body.version, 2)
      assert.equal(body.scene, 2)
      assert.equal(body.openid, 'openid-1')
      return {
        json: async function () {
          return { errcode: 0, result: { suggest: body.content.includes('风险样例') ? 'risky' : 'pass' } }
        }
      }
    }
  })
  const pass = await wechat.check('普通会议纪要', { openid: 'openid-1' })
  assert.equal(pass.ok, true)
  assert.equal(pass.provider, 'wechat-msgSecCheck')
  const risky = await wechat.check('风险样例', { openid: 'openid-1' })
  assert.equal(risky.ok, false)
  assert.equal(risky.code, 'CONTENT_BLOCKED')

  called = 0
  const pipeline = new ContentSafetyPipeline({ local: new LocalKeywordSafety(), wechat: wechat })
  const localBlock = await pipeline.check('儿童色情', { openid: 'openid-1' })
  assert.equal(localBlock.ok, false)
  assert.equal(called, 0)
  const remoteBlock = await pipeline.check('风险样例', { openid: 'openid-1' })
  assert.equal(remoteBlock.provider, 'wechat-msgSecCheck')
  assert.equal(remoteBlock.ok, false)
})
