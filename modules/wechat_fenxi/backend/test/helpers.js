const { createApp } = require('../src/create-app')

async function withApp(options, fn) {
  const app = createApp(options || {})
  const base = await app.listen()
  try {
    await fn(app, base)
  } finally {
    await app.close()
  }
}

async function login(base, code) {
  const res = await fetch(base + '/api/auth/session', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ code: code || 'tester' })
  })
  const json = await res.json()
  if (!res.ok) throw new Error('login failed ' + res.status)
  return json.token
}

function consented(extra) {
  return Object.assign({
    consent: true,
    thirdPartyConsent: true,
    consentVersion: '2026-10-19'
  }, extra || {})
}

async function api(base, token, method, pathname, body, headers) {
  const init = {
    method: method,
    headers: Object.assign({}, headers || {})
  }
  if (token) init.headers.authorization = 'Bearer ' + token
  if (body != null) {
    if (Buffer.isBuffer(body)) {
      init.body = body
    } else if (typeof body === 'string') {
      init.body = body
    } else {
      init.headers['content-type'] = init.headers['content-type'] || 'application/json'
      init.body = JSON.stringify(body)
    }
  }
  const res = await fetch(base + pathname, init)
  const text = await res.text()
  let json = null
  try { json = text ? JSON.parse(text) : null } catch (err) { json = null }
  return { status: res.status, json: json, text: text }
}

async function waitJob(base, token, id) {
  const started = Date.now()
  let last = null
  while (Date.now() - started < 4000) {
    const res = await api(base, token, 'GET', '/api/jobs/' + id)
    last = res
    if (res.json && (res.json.status === 'done' || res.json.status === 'failed')) return res.json
    await new Promise(function (resolve) { setTimeout(resolve, 20) })
  }
  throw new Error('job timeout ' + JSON.stringify(last && last.json))
}

function multipart(fields, file) {
  const boundary = '----schemeAtest'
  const chunks = []
  Object.keys(fields).forEach(function (name) {
    chunks.push(Buffer.from(
      '--' + boundary + '\r\nContent-Disposition: form-data; name="' + name + '"\r\n\r\n' + fields[name] + '\r\n'
    ))
  })
  chunks.push(Buffer.from(
    '--' + boundary + '\r\nContent-Disposition: form-data; name="file"; filename="' + file.filename + '"\r\nContent-Type: application/octet-stream\r\n\r\n'
  ))
  chunks.push(file.data)
  chunks.push(Buffer.from('\r\n--' + boundary + '--\r\n'))
  return {
    body: Buffer.concat(chunks),
    contentType: 'multipart/form-data; boundary=' + boundary
  }
}

const CHAT = [
  '2026-01-02 09:30:00 张三: 会议改到三点，请李四周五前交纪要',
  '2026-01-02 09:31:00 李四: 就这么定了？',
  '2026-01-02 09:32:00 张三: 好，就这么定，周五前交。'
].join('\n')

const GBK_TXT_HEX = '323032362d30312d30322030393a33303a303020d5c5c8fd3a20bbe1d2e9b8c4b5bdc8fdb5e3a3acc7ebc0eecbc4d6dccee5c7b0bdbbbccdd2aa0a323032362d30312d30322030393a33313a303020c0eecbc43a20becdd5e2c3b4b6a8c1cba3bf0a'
const GBK_JSON_HEX = '7b226d65737361676573223a5b7b2273656e646572223a22d5c5c8fd222c2274696d65223a22323032362d30312d30322030393a33303a3030222c22636f6e74656e74223a22bbe1d2e9b8c4b5bdc8fdb5e3a3acc7ebc0eecbc4d6dccee5c7b0bdbbbccdd2aa222c2274797065223a22cec4b1be227d2c7b2273656e646572223a22c0eecbc4222c2274696d65223a22323032362d30312d30322030393a33313a3030222c22636f6e74656e74223a22becdd5e2c3b4b6a8c1cba3bf222c2274797065223a22cec4b1be227d5d7d'
const GBK_MD_HEX = '2320d5c5c8fd0a0a2d20b5bcb3f6c6f7a3ba5765436861742043686174204578706f727420666f72204c4c4d2076312e332e350a2d20bbe1bbb0c0e0d0cda3bacbbdc1c40a2d20cffbcfa2d7dccafda3ba320a0a232320323032362d30312d30320a0a2a2a30393a33303a3030207c20d5c5c8fda3ba2a2a20bbe1d2e9b8c4b5bdc8fdb5e3a3acc7ebc0eecbc4d6dccee5c7b0bdbbbccdd2aa0a0a2a2a30393a33313a3030207c20c0eecbc4a3ba2a2a20becdd5e2c3b4b6a8c1cba3bf0a'

module.exports = {
  withApp: withApp,
  login: login,
  consented: consented,
  api: api,
  waitJob: waitJob,
  multipart: multipart,
  CHAT: CHAT,
  GBK_TXT_HEX: GBK_TXT_HEX,
  GBK_JSON_HEX: GBK_JSON_HEX,
  GBK_MD_HEX: GBK_MD_HEX
}
