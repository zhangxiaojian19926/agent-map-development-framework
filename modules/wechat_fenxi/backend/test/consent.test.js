const test = require('node:test')
const assert = require('node:assert/strict')
const policy = require('../../miniprogram/utils/import-policy')
const { withApp, login, consented, api, multipart, CHAT } = require('./helpers')

test('jobs, presign, and multipart upload all refuse missing consent', async function () {
  await withApp({}, async function (app, base) {
    const token = await login(base)
    const noConsent = await api(base, token, 'POST', '/api/jobs', {
      source: 'paste',
      text: CHAT
    })
    assert.equal(noConsent.status, 403)
    assert.equal(noConsent.json.error.code, 'CONSENT_REQUIRED')

    const half = await api(base, token, 'POST', '/api/jobs', {
      source: 'paste',
      text: CHAT,
      consent: true,
      thirdPartyConsent: false
    })
    assert.equal(half.status, 403)
    assert.equal(app.store.stats().jobs, 0)

    const presign = await api(base, token, 'POST', '/api/storage/presign', {
      filename: 'paste.txt',
      bytes: 12,
      consent: false,
      thirdPartyConsent: true
    })
    assert.equal(presign.status, 403)
    assert.equal(app.store.stats().uploads, 0)

    const form = multipart({ consent: 'false', thirdPartyConsent: 'true' }, {
      filename: 'chat.txt',
      data: Buffer.from(CHAT, 'utf8')
    })
    const upload = await api(base, token, 'POST', '/api/uploads', form.body, {
      'content-type': form.contentType
    })
    assert.equal(upload.status, 403)
    assert.equal(app.store.stats().uploads, 0)
  })
})

test('client submit plan is closed until both consent boxes are checked', function () {
  const missing = policy.buildSubmitPlan({
    mode: 'paste',
    text: '张三: 你好，今天对一下。',
    consent: false,
    thirdPartyConsent: true
  })
  assert.equal(missing.ok, false)
  assert.equal(missing.code, 'CONSENT_REQUIRED')
  const ready = policy.buildSubmitPlan({
    mode: 'paste',
    text: '张三: 你好，今天对一下。',
    consent: true,
    thirdPartyConsent: true
  })
  assert.equal(ready.ok, true)
})

test('a consented paste creates a job', async function () {
  await withApp({}, async function (app, base) {
    const token = await login(base)
    const created = await api(base, token, 'POST', '/api/jobs', consented({ source: 'paste', text: CHAT }))
    assert.equal(created.status, 202)
    assert.equal(app.store.stats().jobs, 1)
  })
})
