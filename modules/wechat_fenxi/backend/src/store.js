const crypto = require('crypto')

function createStore(options) {
  const now = options.now
  const jobs = new Map()
  const uploads = new Map()

  function sweep() {
    const clock = now()
    for (const [id, job] of jobs) {
      if (job.expiresAt <= clock) eraseJob(id)
    }
    for (const [id, upload] of uploads) {
      if (upload.expiresAt <= clock && !upload.pinned) uploads.delete(id)
    }
  }

  function eraseJob(id) {
    const job = jobs.get(id)
    if (!job) return null
    jobs.delete(id)
    if (job.uploadId) uploads.delete(job.uploadId)
    return job
  }

  return {
    sweep: sweep,
    createUpload: function (fields) {
      const id = crypto.randomBytes(16).toString('hex')
      const upload = {
        id: id,
        owner: fields.owner,
        token: crypto.randomBytes(16).toString('hex'),
        filename: fields.filename,
        declaredBytes: fields.declaredBytes,
        source: fields.source,
        ready: false,
        bytes: null,
        createdAt: now(),
        expiresAt: now() + fields.ttlMs,
        pinned: false
      }
      uploads.set(id, upload)
      return upload
    },
    getUpload: function (id) {
      return uploads.get(id) || null
    },
    deleteUpload: function (id) {
      uploads.delete(id)
    },
    createJob: function (fields) {
      const id = crypto.randomBytes(16).toString('hex')
      const job = {
        id: id,
        owner: fields.owner,
        status: 'pending',
        statusLog: ['pending'],
        source: fields.source,
        uploadId: fields.uploadId || null,
        filename: fields.filename || '',
        inlineText: fields.inlineText || null,
        messages: null,
        result: null,
        error: null,
        encoding: null,
        format: null,
        messageCount: 0,
        chunkCount: 0,
        consentVersion: fields.consentVersion || '',
        createdAt: now(),
        expiresAt: now() + fields.ttlMs
      }
      jobs.set(id, job)
      if (job.uploadId && uploads.has(job.uploadId)) uploads.get(job.uploadId).pinned = true
      return job
    },
    getJob: function (id) {
      return jobs.get(id) || null
    },
    eraseJob: eraseJob,
    deleteUser: function (owner) {
      let removed = 0
      let removedBytes = 0
      for (const [id, job] of jobs) {
        if (job.owner !== owner) continue
        removedBytes += byteSizeOfJob(job)
        if (job.uploadId && uploads.has(job.uploadId) && uploads.get(job.uploadId).bytes) {
          removedBytes += uploads.get(job.uploadId).bytes.length
        }
        eraseJob(id)
        removed += 1
      }
      for (const [id, upload] of uploads) {
        if (upload.owner !== owner) continue
        removedBytes += upload.bytes ? upload.bytes.length : 0
        uploads.delete(id)
      }
      return { removed: removed, removedBytes: removedBytes }
    },
    stats: function () {
      return { jobs: jobs.size, uploads: uploads.size }
    }
  }
}

function byteSizeOfJob(job) {
  let n = 0
  if (job.inlineText) n += Buffer.byteLength(job.inlineText)
  if (job.uploadId) n += 0
  return n
}

function publicJob(job) {
  return {
    id: job.id,
    status: job.status,
    statusLog: job.statusLog.slice(),
    error: job.error,
    result: job.result,
    messageCount: job.messageCount,
    chunkCount: job.chunkCount,
    encoding: job.encoding,
    format: job.format,
    source: job.source,
    filename: job.filename,
    createdAt: job.createdAt,
    expiresAt: job.expiresAt,
    consentVersion: job.consentVersion
  }
}

module.exports = { createStore, publicJob }
