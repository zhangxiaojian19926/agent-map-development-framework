const { parseUpload } = require('./parse')
const { decodeBytes } = require('./encoding')
const { chunkMessages } = require('./chunk')
const { assertSummary } = require('./schema')
const { fail } = require('./errors')

function kickJob(job, deps) {
  setImmediate(function () {
    processJob(job, deps).catch(function (err) {
      markFailed(job, deps, err)
    })
  })
}

async function processJob(job, deps) {
  const store = deps.store
  await deps.pause()
  if (!stillThere(store, job)) return

  setStatus(job, 'parsing')
  await deps.pause()
  if (!stillThere(store, job)) return

  const loaded = loadText(job, store)
  job.encoding = loaded.encoding
  job.filename = loaded.filename || job.filename
  const parsed = parseUpload({ text: loaded.text, filename: loaded.filename })
  job.messages = parsed.messages
  job.messageCount = parsed.messages.length
  job.format = parsed.format

  const safetyText = parsed.messages.map(function (message) {
    return message.sender + ': ' + message.content
  }).join('\n')
  const verdict = await deps.safety.check(safetyText, { openid: job.owner, jobId: job.id })
  if (!verdict.ok) {
    const err = fail(400, verdict.code || 'CONTENT_BLOCKED', verdict.message || '内容未通过安全检查')
    err.ruleId = verdict.ruleId || null
    err.provider = verdict.provider
    throw err
  }

  setStatus(job, 'summarizing')
  await deps.pause()
  if (!stillThere(store, job)) return

  const chunks = chunkMessages(parsed.messages, deps.chunkCharBudget)
  job.chunkCount = chunks.length
  const partials = []
  for (const chunk of chunks) {
    partials.push(await withRetry(function () {
      return deps.llm.summarizeChunk(chunk, { jobId: job.id })
    }, 2))
  }
  const merged = partials.length === 1
    ? partials[0]
    : await withRetry(function () {
      return deps.llm.mergeSummaries(partials, parsed.messages)
    }, 2)
  job.result = assertSummary(merged)
  setStatus(job, 'done')
}

function loadText(job, store) {
  if (job.uploadId) {
    const upload = store.getUpload(job.uploadId)
    if (!upload || upload.owner !== job.owner || !upload.ready || !upload.bytes) {
      throw fail(400, 'UPLOAD_NOT_FOUND', '找不到已上传的文件')
    }
    const decoded = decodeBytes(upload.bytes)
    return { text: decoded.text, encoding: decoded.encoding, filename: upload.filename }
  }
  if (typeof job.inlineText === 'string') {
    return { text: job.inlineText, encoding: 'utf-8', filename: job.filename || 'paste.txt' }
  }
  throw fail(400, 'EMPTY_INPUT', '没有可读内容')
}

async function withRetry(fn, times) {
  let last
  for (let attempt = 0; attempt < times; attempt++) {
    try {
      return await fn(attempt)
    } catch (err) {
      last = err
    }
  }
  throw last
}

function setStatus(job, status) {
  job.status = status
  job.statusLog.push(status)
}

function stillThere(store, job) {
  return store.getJob(job.id) === job
}

function markFailed(job, deps, err) {
  if (!stillThere(deps.store, job)) return
  if (job.status === 'done') return
  job.error = {
    code: err.code || 'FAILED',
    message: err.message || '分析失败',
    ruleId: err.ruleId || null,
    provider: err.provider || null
  }
  setStatus(job, 'failed')
}

module.exports = { kickJob, processJob }
