const http = require('http')
const path = require('path')
const limits = require('../../miniprogram/utils/limits')
const { fail } = require('./errors')
const { createStore, publicJob } = require('./store')
const { kickJob } = require('./jobs')
const { parseMultipart } = require('./multipart')
const { MockLlmProvider, buildLlmFromEnv } = require('./llm')
const { buildSafetyFromEnv } = require('./safety')
const { buildSessionExchanger, createTokenStore } = require('./auth')

function createApp(options) {
  const opts = options || {}
  const now = opts.now || function () { return Date.now() }
  const ttlMs = opts.ttlMs == null ? limits.TTL_MS : opts.ttlMs
  const store = createStore({ now: now })
  const runtimeEnv = opts.env || {}
  const llm = opts.llm || buildLlmFromEnv(runtimeEnv)
  const safety = opts.safety || buildSafetyFromEnv(runtimeEnv)
  const sessions = opts.sessions || buildSessionExchanger(runtimeEnv)
  const tokens = createTokenStore(now)
  const chunkCharBudget = opts.chunkCharBudget || 4000
  const gate = opts.gates ? createGate() : null

  function pause() {
    if (!gate) return Promise.resolve()
    return gate.wait()
  }

  const deps = {
    store: store,
    llm: llm,
    safety: safety,
    pause: pause,
    chunkCharBudget: chunkCharBudget
  }

  const server = http.createServer(function (req, res) {
    handle(req, res).catch(function (err) {
      if (res.headersSent || res.writableEnded) return
      const status = err.status || 500
      if (status === 500) console.error(err)
      sendJson(res, status, {
        error: {
          code: err.code || 'INTERNAL',
          message: status === 500 ? '服务器错误' : err.message
        }
      })
    })
  })

  async function handle(req, res) {
    store.sweep()
    const url = new URL(req.url, 'http://127.0.0.1')
    const pathname = url.pathname
    if (req.method === 'GET' && pathname === '/api/health') {
      return sendJson(res, 200, { ok: true, notify: 'poll' })
    }
    if (req.method === 'GET' && pathname === '/api/policy') {
      return sendJson(res, 200, {
        pasteInlineMaxBytes: limits.PASTE_INLINE_MAX_BYTES,
        fileMaxBytes: limits.FILE_MAX_BYTES,
        jobsJsonMaxBytes: limits.JOBS_JSON_MAX_BYTES,
        ttlMs: ttlMs,
        ttlHours: Math.round(ttlMs / 3600000),
        allowedExt: limits.ALLOWED_EXT,
        consentVersion: limits.CONSENT_VERSION,
        notify: 'poll',
        subscribeMessageRequired: false
      })
    }
    if (req.method === 'POST' && pathname === '/api/auth/session') {
      const body = await readJson(req, 16 * 1024)
      const exchanged = await sessions.exchange(body.code)
      const token = tokens.issue(exchanged.openid)
      return sendJson(res, 200, { token: token, openid: exchanged.openid })
    }

    const objectMatch = pathname.match(/^\/api\/storage\/objects\/([a-f0-9]{32})$/)
    if (objectMatch && req.method === 'PUT') {
      const upload = store.getUpload(objectMatch[1])
      if (!upload) throw fail(404, 'UPLOAD_NOT_FOUND', '找不到上传任务')
      const token = String(req.headers['x-upload-token'] || '')
      if (token !== upload.token) throw fail(403, 'UPLOAD_TOKEN', '直传凭证不正确')
      const bytes = await readBody(req, limits.FILE_MAX_BYTES)
      if (bytes.length === 0) throw fail(400, 'EMPTY_INPUT', '没有可读内容')
      if (bytes.length > upload.declaredBytes) {
        throw fail(413, 'PAYLOAD_TOO_LARGE', '直传内容超过申报大小')
      }
      upload.bytes = bytes
      upload.ready = true
      return sendJson(res, 200, { uploadId: upload.id, bytes: bytes.length, ready: true })
    }

    const session = requireSession(req)
    if (req.method === 'DELETE' && pathname === '/api/me/data') {
      const result = store.deleteUser(session.openid)
      return sendJson(res, 200, {
        deleted: true,
        removedJobs: result.removed,
        removedBytes: result.removedBytes
      })
    }
    if (req.method === 'POST' && pathname === '/api/storage/presign') {
      const body = await readJson(req, 16 * 1024)
      assertConsent(body)
      const filename = safeFilename(body.filename || 'paste.txt')
      assertAllowedFilename(filename)
      const declared = Number(body.bytes)
      if (!Number.isFinite(declared) || declared <= 0) throw fail(400, 'EMPTY_INPUT', '没有可读内容')
      if (declared > limits.FILE_MAX_BYTES) throw fail(413, 'FILE_TOO_LARGE', '单个文件不能超过 10MB')
      const upload = store.createUpload({
        owner: session.openid,
        filename: filename,
        declaredBytes: declared,
        source: body.source === 'file' ? 'file' : 'paste',
        ttlMs: ttlMs
      })
      const absolute = publicOrigin(req) + '/api/storage/objects/' + upload.id
      return sendJson(res, 200, {
        uploadId: upload.id,
        method: 'PUT',
        url: absolute,
        headers: { 'x-upload-token': upload.token },
        maxBytes: limits.FILE_MAX_BYTES,
        declaredBytes: declared
      })
    }
    if (req.method === 'POST' && pathname === '/api/uploads') {
      const raw = await readBody(req, limits.FILE_MAX_BYTES + 64 * 1024)
      const parts = parseMultipart(raw, req.headers['content-type'])
      const fields = {}
      let file = null
      for (const part of parts) {
        if (part.filename) file = part
        else if (part.name) fields[part.name] = part.data.toString('utf8')
      }
      assertConsentFlags(fields.consent, fields.thirdPartyConsent)
      if (!file) throw fail(400, 'NO_FILE', '没有文件')
      const filename = safeFilename(file.filename)
      assertAllowedFilename(filename)
      if (file.data.length === 0) throw fail(400, 'EMPTY_INPUT', '文件是空的')
      if (file.data.length > limits.FILE_MAX_BYTES) throw fail(413, 'FILE_TOO_LARGE', '单个文件不能超过 10MB')
      const upload = store.createUpload({
        owner: session.openid,
        filename: filename,
        declaredBytes: file.data.length,
        source: 'file',
        ttlMs: ttlMs
      })
      upload.bytes = file.data
      upload.ready = true
      return sendJson(res, 201, { uploadId: upload.id, bytes: file.data.length, filename: filename })
    }
    if (req.method === 'POST' && pathname === '/api/jobs') {
      const raw = await readBody(req, limits.JOBS_JSON_MAX_BYTES)
      let body
      try {
        body = JSON.parse(raw.toString('utf8') || '{}')
      } catch (err) {
        throw fail(400, 'INVALID_JSON', '请求不是 JSON')
      }
      if (body && typeof body === 'object' && typeof body.text === 'string') {
        const textBytes = Buffer.byteLength(body.text, 'utf8')
        if (textBytes > limits.PASTE_INLINE_MAX_BYTES) {
          throw fail(413, 'OVERSIZE_USE_STORAGE', '粘贴超过 ' + limits.PASTE_INLINE_MAX_BYTES + ' 字节，请改走存储直传，不要把全文放进这个请求')
        }
      }
      assertConsent(body)
      if (body.text && body.uploadId) throw fail(400, 'AMBIGUOUS_INPUT', '请只提交文本或文件其中一种')
      let filename = ''
      let inlineText = null
      let uploadId = null
      const source = body.source === 'file' ? 'file' : 'paste'
      if (body.uploadId) {
        if (!/^[a-f0-9]{32}$/.test(String(body.uploadId))) throw fail(400, 'UPLOAD_NOT_FOUND', '找不到已上传的文件')
        const upload = store.getUpload(String(body.uploadId))
        if (!upload || upload.owner !== session.openid || !upload.ready) {
          throw fail(400, 'UPLOAD_NOT_FOUND', '找不到已上传的文件')
        }
        uploadId = upload.id
        filename = upload.filename
      } else if (typeof body.text === 'string') {
        if (!body.text.trim()) throw fail(400, 'EMPTY_INPUT', '没有可读内容')
        inlineText = body.text
        filename = 'paste.txt'
      } else {
        throw fail(400, 'EMPTY_INPUT', '没有可读内容')
      }
      const job = store.createJob({
        owner: session.openid,
        source: source,
        uploadId: uploadId,
        filename: filename,
        inlineText: inlineText,
        consentVersion: String(body.consentVersion || limits.CONSENT_VERSION),
        ttlMs: ttlMs
      })
      kickJob(job, deps)
      return sendJson(res, 202, publicJob(job))
    }
    const jobMatch = pathname.match(/^\/api\/jobs\/([a-f0-9]{32})$/)
    if (jobMatch && req.method === 'GET') {
      const job = store.getJob(jobMatch[1])
      if (!job || job.owner !== session.openid) throw fail(404, 'NOT_FOUND', '找不到这个任务')
      return sendJson(res, 200, publicJob(job))
    }
    if (jobMatch && req.method === 'DELETE') {
      const job = store.getJob(jobMatch[1])
      if (!job || job.owner !== session.openid) throw fail(404, 'NOT_FOUND', '找不到这个任务')
      const removedBytes = job.inlineText ? Buffer.byteLength(job.inlineText) : 0
      const upload = job.uploadId ? store.getUpload(job.uploadId) : null
      const uploadBytes = upload && upload.bytes ? upload.bytes.length : 0
      store.eraseJob(job.id)
      return sendJson(res, 200, { deleted: true, id: jobMatch[1], removedBytes: removedBytes + uploadBytes })
    }
    throw fail(404, 'NOT_FOUND', '没有这个接口')
  }

  function requireSession(req) {
    const header = String(req.headers.authorization || '')
    const match = /^Bearer\s+(.+)$/i.exec(header)
    if (!match) throw fail(401, 'UNAUTHORIZED', '请先登录')
    const row = tokens.read(match[1].trim())
    if (!row) throw fail(401, 'UNAUTHORIZED', '登录已失效')
    return row
  }

  return {
    server: server,
    store: store,
    llm: llm,
    release: function () {
      if (gate) gate.release()
    },
    listen: function () {
      return new Promise(function (resolve) {
        server.listen(0, '127.0.0.1', function () {
          const port = server.address().port
          resolve('http://127.0.0.1:' + port)
        })
      })
    },
    close: function () {
      return new Promise(function (resolve) { server.close(function () { resolve() }) })
    }
  }
}

function assertConsent(body) {
  if (!body || typeof body !== 'object') throw fail(400, 'INVALID_JSON', '请求不是 JSON')
  assertConsentFlags(body.consent, body.thirdPartyConsent)
}

function assertConsentFlags(consent, third) {
  const okConsent = consent === true || consent === 'true'
  const okThird = third === true || third === 'true'
  if (!okConsent || !okThird) {
    throw fail(403, 'CONSENT_REQUIRED', '请先同意隐私说明，并确认有权提交这些内容')
  }
}

function assertAllowedFilename(filename) {
  const ext = path.extname(filename).slice(1).toLowerCase()
  if (limits.ALLOWED_EXT.indexOf(ext) < 0) {
    throw fail(400, 'UNSUPPORTED_TYPE', '仅支持 txt、json、md。不接收数据库文件。')
  }
}

function safeFilename(name) {
  const base = path.basename(String(name || 'paste.txt')).replace(/[^\w.\-\u4e00-\u9fff]+/g, '_')
  return base.slice(0, 180) || 'paste.txt'
}

function publicOrigin(req) {
  const proto = String(req.headers['x-forwarded-proto'] || 'http').split(',')[0].trim()
  const host = req.headers.host || '127.0.0.1'
  return proto + '://' + host
}

function readBody(req, maxBytes) {
  return new Promise(function (resolve, reject) {
    let settled = false
    function finish(err, value) {
      if (settled) return
      settled = true
      if (err) reject(err)
      else resolve(value)
    }
    const tooLarge = fail(413, 'PAYLOAD_TOO_LARGE', '请求体超过上限。长文本请改走存储直传。')
    const declared = Number(req.headers['content-length'] || 0)
    if (declared > maxBytes) {
      req.resume()
      finish(tooLarge)
      return
    }
    const chunks = []
    let total = 0
    req.on('data', function (chunk) {
      total += chunk.length
      if (total > maxBytes) {
        req.pause()
        req.resume()
        finish(tooLarge)
        return
      }
      chunks.push(chunk)
    })
    req.on('end', function () { finish(null, Buffer.concat(chunks)) })
    req.on('error', function (err) { finish(err) })
  })
}

function readJson(req, maxBytes) {
  return readBody(req, maxBytes).then(function (buf) {
    if (!buf.length) return {}
    try {
      return JSON.parse(buf.toString('utf8'))
    } catch (err) {
      throw fail(400, 'INVALID_JSON', '请求不是 JSON')
    }
  })
}

function sendJson(res, status, body) {
  const payload = Buffer.from(JSON.stringify(body))
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': payload.length,
    'cache-control': 'no-store'
  })
  res.end(payload)
}

function createGate() {
  const queue = []
  let open = 0
  return {
    wait: function () {
      if (open > 0) {
        open -= 1
        return Promise.resolve()
      }
      return new Promise(function (resolve) { queue.push(resolve) })
    },
    release: function () {
      const next = queue.shift()
      if (next) next()
      else open += 1
    }
  }
}

module.exports = { createApp }
