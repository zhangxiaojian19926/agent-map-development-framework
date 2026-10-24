const test = require('node:test')
const assert = require('node:assert/strict')
const fs = require('fs')
const path = require('path')
const { withApp, login, consented, api, waitJob, multipart, CHAT, GBK_TXT_HEX } = require('./helpers')

function settle() {
  return new Promise(function (resolve) { setImmediate(resolve) })
}

async function until(fn) {
  const started = Date.now()
  while (Date.now() - started < 2000) {
    if (await fn()) return
    await settle()
  }
  throw new Error('status did not change')
}

test('polling observes pending, parsing, summarizing, then done', async function () {
  await withApp({ gates: true }, async function (app, base) {
    const token = await login(base)
    const created = await api(base, token, 'POST', '/api/jobs', consented({ source: 'paste', text: CHAT }))
    assert.equal(created.status, 202)
    assert.equal(created.json.status, 'pending')
    await until(async function () {
      const current = await api(base, token, 'GET', '/api/jobs/' + created.json.id)
      return current.json.status === 'pending' && current.json.statusLog.length === 1
    })
    for (let i = 0; i < 5; i++) await settle()
    const still = await api(base, token, 'GET', '/api/jobs/' + created.json.id)
    assert.equal(still.json.status, 'pending')

    app.release()
    await until(async function () {
      const current = await api(base, token, 'GET', '/api/jobs/' + created.json.id)
      return current.json.status === 'parsing'
    })
    app.release()
    await until(async function () {
      const current = await api(base, token, 'GET', '/api/jobs/' + created.json.id)
      return current.json.status === 'summarizing'
    })
    app.release()
    await until(async function () {
      const current = await api(base, token, 'GET', '/api/jobs/' + created.json.id)
      return current.json.status === 'done'
    })
    const done = await api(base, token, 'GET', '/api/jobs/' + created.json.id)
    assert.deepEqual(done.json.statusLog, ['pending', 'parsing', 'summarizing', 'done'])
  })
})

test('GBK file upload reaches done through multipart, not a raw JSON paste', async function () {
  await withApp({}, async function (app, base) {
    const token = await login(base)
    const form = multipart({ consent: 'true', thirdPartyConsent: 'true' }, {
      filename: 'chat_full_for_llm.txt',
      data: Buffer.from(GBK_TXT_HEX, 'hex')
    })
    const upload = await api(base, token, 'POST', '/api/uploads', form.body, { 'content-type': form.contentType })
    assert.equal(upload.status, 201)
    const created = await api(base, token, 'POST', '/api/jobs', consented({
      source: 'file',
      uploadId: upload.json.uploadId
    }))
    const job = await waitJob(base, token, created.json.id)
    assert.equal(job.status, 'done')
    assert.equal(job.encoding, 'gbk')
    assert.equal(job.messageCount, 2)
    assert.deepEqual(job.result.participants, ['张三', '李四'])
    assert.equal(job.statusLog[0], 'pending')
    assert.equal(job.statusLog[job.statusLog.length - 1], 'done')
  })
})

test('empty paste is rejected and garbage becomes a failed job', async function () {
  await withApp({}, async function (app, base) {
    const token = await login(base)
    const empty = await api(base, token, 'POST', '/api/jobs', consented({ source: 'paste', text: '   \n' }))
    assert.equal(empty.status, 400)
    assert.equal(empty.json.error.code, 'EMPTY_INPUT')
    assert.equal(app.store.stats().jobs, 0)

    const garbage = await api(base, token, 'POST', '/api/jobs', consented({ source: 'paste', text: '@@@###$$$' }))
    const job = await waitJob(base, token, garbage.json.id)
    assert.equal(job.status, 'failed')
    assert.equal(job.error.code, 'UNRECOGNIZED_INPUT')
    assert.equal(app.llm.calls.length, 0)
  })
})

test('there is no subscribe-message API; the mini program polls', async function () {
  await withApp({}, async function (app, base) {
    const token = await login(base)
    const missing = await api(base, token, 'POST', '/api/subscribe', {})
    assert.equal(missing.status, 404)
    const policy = await api(base, '', 'GET', '/api/policy')
    assert.equal(policy.json.notify, 'poll')
    assert.equal(policy.json.subscribeMessageRequired, false)
  })
  const jobJs = fs.readFileSync(path.join(__dirname, '../../miniprogram/pages/job/job.js'), 'utf8')
  assert.match(jobJs, /setInterval/)
  assert.match(jobJs, /getJob/)
  assert.equal(jobJs.includes('requestSubscribeMessage'), false)
})
