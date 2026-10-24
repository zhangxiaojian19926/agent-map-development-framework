const test = require('node:test')
const assert = require('node:assert/strict')
const { withApp, login, consented, api, waitJob, multipart, CHAT } = require('./helpers')

test('delete one job removes source and result; another user cannot see it', async function () {
  await withApp({}, async function (app, base) {
    const token = await login(base, 'owner')
    const other = await login(base, 'other')
    const created = await api(base, token, 'POST', '/api/jobs', consented({ source: 'paste', text: CHAT }))
    const job = await waitJob(base, token, created.json.id)
    assert.equal(job.status, 'done')
    assert.equal(app.store.getJob(job.id).inlineText.includes('纪要'), true)

    const hidden = await api(base, other, 'GET', '/api/jobs/' + job.id)
    assert.equal(hidden.status, 404)

    const removed = await api(base, token, 'DELETE', '/api/jobs/' + job.id)
    assert.equal(removed.status, 200)
    assert.equal(removed.json.deleted, true)
    assert.equal(removed.json.removedBytes > 0, true)
    assert.equal(app.store.getJob(job.id), null)
    const again = await api(base, token, 'GET', '/api/jobs/' + job.id)
    assert.equal(again.status, 404)
  })
})

test('delete-my-data removes every job and uploaded file for that account', async function () {
  await withApp({}, async function (app, base) {
    const token = await login(base, 'owner')
    const other = await login(base, 'other')
    const form = multipart({ consent: 'true', thirdPartyConsent: 'true' }, {
      filename: 'chat.txt',
      data: Buffer.from(CHAT, 'utf8')
    })
    const upload = await api(base, token, 'POST', '/api/uploads', form.body, { 'content-type': form.contentType })
    assert.equal(upload.status, 201)
    const fileJob = await api(base, token, 'POST', '/api/jobs', consented({
      source: 'file',
      uploadId: upload.json.uploadId
    }))
    const pasteJob = await api(base, token, 'POST', '/api/jobs', consented({ source: 'paste', text: CHAT }))
    await waitJob(base, token, fileJob.json.id)
    await waitJob(base, token, pasteJob.json.id)
    const kept = await api(base, other, 'POST', '/api/jobs', consented({ source: 'paste', text: CHAT }))
    await waitJob(base, other, kept.json.id)

    const deleted = await api(base, token, 'DELETE', '/api/me/data')
    assert.equal(deleted.status, 200)
    assert.equal(deleted.json.removedJobs, 2)
    assert.equal(app.store.getJob(fileJob.json.id), null)
    assert.equal(app.store.getUpload(upload.json.uploadId), null)
    assert.equal(app.store.getJob(kept.json.id).owner !== '', true)
    assert.equal((await api(base, token, 'GET', '/api/jobs/' + pasteJob.json.id)).status, 404)
    assert.equal((await api(base, other, 'GET', '/api/jobs/' + kept.json.id)).json.status, 'done')
  })
})

test('TTL sweep drops the job and its upload', async function () {
  let now = 1_700_000_000_000
  await withApp({ ttlMs: 1000, now: function () { return now } }, async function (app, base) {
    const token = await login(base)
    const form = multipart({ consent: 'true', thirdPartyConsent: 'true' }, {
      filename: 'chat.txt',
      data: Buffer.from(CHAT, 'utf8')
    })
    const upload = await api(base, token, 'POST', '/api/uploads', form.body, { 'content-type': form.contentType })
    const created = await api(base, token, 'POST', '/api/jobs', consented({
      source: 'file',
      uploadId: upload.json.uploadId
    }))
    const job = await waitJob(base, token, created.json.id)
    assert.equal(job.status, 'done')
    now += 5000
    const gone = await api(base, token, 'GET', '/api/jobs/' + job.id)
    assert.equal(gone.status, 404)
    assert.equal(app.store.stats().jobs, 0)
    assert.equal(app.store.getUpload(upload.json.uploadId), null)
  })
})
