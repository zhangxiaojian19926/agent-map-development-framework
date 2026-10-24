const test = require('node:test')
const assert = require('node:assert/strict')
const limits = require('../../miniprogram/utils/limits')
const policy = require('../../miniprogram/utils/import-policy')
const { withApp, login, consented, api, waitJob } = require('./helpers')

test('small paste is accepted inline and oversize paste is refused on POST /api/jobs', async function () {
  await withApp({}, async function (app, base) {
    const token = await login(base)
    const small = await api(base, token, 'POST', '/api/jobs', consented({
      source: 'paste',
      text: '2026-01-02 09:30:00 张三: 今天下午对一下纪要'
    }))
    assert.equal(small.status, 202)
    const done = await waitJob(base, token, small.json.id)
    assert.equal(done.status, 'done')
    assert.equal(app.llm.calls.length > 0, true)

    const callsBefore = app.llm.calls.length
    const big = 'a'.repeat(limits.PASTE_INLINE_MAX_BYTES + 4096)
    const over = await api(base, token, 'POST', '/api/jobs', consented({ source: 'paste', text: big }))
    assert.equal(over.status, 413)
    assert.equal(over.json.error.code, 'OVERSIZE_USE_STORAGE')
    assert.equal(app.store.stats().jobs, 1)
    assert.equal(app.llm.calls.length, callsBefore)

    const huge = 'b'.repeat(limits.JOBS_JSON_MAX_BYTES + 2048)
    const capped = await api(base, token, 'POST', '/api/jobs', consented({ source: 'paste', text: huge }))
    assert.equal(capped.status, 413)
    assert.equal(capped.json.error.code, 'PAYLOAD_TOO_LARGE')
    assert.equal(app.store.stats().jobs, 1)
  })
})

test('oversize paste succeeds only through direct-to-storage, and the job body has no text', async function () {
  await withApp({}, async function (app, base) {
    const token = await login(base)
    const text = '会议纪要垫字。' + '甲'.repeat(30000)
    assert.equal(Buffer.byteLength(text, 'utf8') > limits.PASTE_INLINE_MAX_BYTES, true)
    const plan = policy.buildSubmitPlan({
      mode: 'paste',
      text: text,
      consent: true,
      thirdPartyConsent: true
    })
    assert.equal(plan.channel, 'storage')
    assert.throws(function () { policy.jobPayload(plan) }, function (err) { return err.code === 'MISSING_UPLOAD' })

    const presign = await api(base, token, 'POST', '/api/storage/presign', consented({
      filename: 'paste.txt',
      bytes: Buffer.byteLength(text, 'utf8'),
      source: 'paste'
    }))
    assert.equal(presign.status, 200)
    assert.equal(presign.json.method, 'PUT')
    const put = await fetch(presign.json.url, {
      method: 'PUT',
      headers: presign.json.headers,
      body: text
    })
    assert.equal(put.status, 200)

    const payload = policy.jobPayload(Object.assign({}, plan, { uploadId: presign.json.uploadId }))
    assert.equal(Object.prototype.hasOwnProperty.call(payload, 'text'), false)
    assert.equal(payload.uploadId, presign.json.uploadId)

    const created = await api(base, token, 'POST', '/api/jobs', payload)
    assert.equal(created.status, 202)
    const job = await waitJob(base, token, created.json.id)
    assert.equal(job.status, 'done')
    assert.equal(job.encoding, 'utf-8')
    assert.equal(job.messageCount >= 1, true)
    assert.equal(app.store.getJob(job.id).inlineText, null)
    assert.equal(app.store.getUpload(presign.json.uploadId).bytes.toString('utf8'), text)
  })
})

test('client inline plan stays under the threshold and never labels oversize as inline', function () {
  const small = policy.planPaste('你好')
  assert.equal(small.channel, 'inline')
  const over = policy.planPaste('字'.repeat(Math.ceil(limits.PASTE_INLINE_MAX_BYTES / 2)))
  assert.equal(over.channel, 'storage')
  const inline = policy.buildSubmitPlan({
    mode: 'paste',
    text: '张三: 你好，这是一段足够长的粘贴。',
    consent: true,
    thirdPartyConsent: true
  })
  const body = policy.jobPayload(inline)
  assert.equal(body.text.includes('你好'), true)
  assert.throws(function () {
    policy.jobPayload(Object.assign({}, inline, { bytes: limits.PASTE_INLINE_MAX_BYTES + 1 }))
  }, function (err) { return err.code === 'OVERSIZE_USE_STORAGE' })
})
