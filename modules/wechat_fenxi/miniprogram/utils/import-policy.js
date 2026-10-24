const limits = require('./limits')

function utf8ByteLength(text) {
  const s = String(text == null ? '' : text)
  let n = 0
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i)
    if (c <= 0x7f) n += 1
    else if (c <= 0x7ff) n += 2
    else if (c >= 0xd800 && c <= 0xdbff) {
      n += 4
      i += 1
    } else n += 3
  }
  return n
}

function planPaste(text) {
  const value = String(text == null ? '' : text)
  const bytes = utf8ByteLength(value)
  return {
    bytes: bytes,
    channel: bytes > limits.PASTE_INLINE_MAX_BYTES ? 'storage' : 'inline',
    text: value
  }
}

function limitLabel() {
  const kb = Math.round(limits.PASTE_INLINE_MAX_BYTES / 1024)
  const mb = Math.round(limits.FILE_MAX_BYTES / (1024 * 1024))
  return '普通提交上限 ' + kb + 'KB；更长的粘贴改走存储直传。单个文件上限 ' + mb + 'MB。'
}

/**
 * Decide whether the user may submit, and which channel carries the bytes.
 * Oversize paste never returns an inline JSON body.
 */
function buildSubmitPlan(input) {
  const consent = !!(input && input.consent)
  const thirdPartyConsent = !!(input && input.thirdPartyConsent)
  if (!consent || !thirdPartyConsent) {
    return {
      ok: false,
      code: 'CONSENT_REQUIRED',
      message: '请先勾选隐私说明，并确认有权提交这些内容'
    }
  }
  const mode = input.mode === 'file' ? 'file' : 'paste'
  if (mode === 'paste') {
    const text = String(input.text || '')
    if (!text.trim()) {
      return { ok: false, code: 'EMPTY_INPUT', message: '请先粘贴聊天文本' }
    }
    const planned = planPaste(text)
    if (planned.channel === 'storage') {
      return {
        ok: true,
        channel: 'storage',
        source: 'paste',
        bytes: planned.bytes,
        text: text
      }
    }
    return {
      ok: true,
      channel: 'inline',
      source: 'paste',
      bytes: planned.bytes,
      text: text
    }
  }
  const file = input.file
  if (!file || !file.name) {
    return { ok: false, code: 'NO_FILE', message: '请从会话里选择 txt、json 或 md 文件' }
  }
  const ext = extensionOf(file.name)
  if (limits.ALLOWED_EXT.indexOf(ext) < 0) {
    return { ok: false, code: 'UNSUPPORTED_TYPE', message: '仅支持 txt、json、md' }
  }
  const size = Number(file.size || 0)
  if (size > limits.FILE_MAX_BYTES) {
    return { ok: false, code: 'FILE_TOO_LARGE', message: '单个文件不能超过 10MB' }
  }
  if (size <= 0) {
    return { ok: false, code: 'EMPTY_INPUT', message: '文件是空的' }
  }
  return {
    ok: true,
    channel: 'file',
    source: 'file',
    bytes: size,
    file: file
  }
}

function extensionOf(name) {
  const base = String(name || '').split(/[/\\]/).pop()
  const dot = base.lastIndexOf('.')
  if (dot <= 0) return ''
  return base.slice(dot + 1).toLowerCase()
}

/**
 * JSON body for POST /api/jobs. Inline channel is the only one allowed to carry text,
 * and only under the byte threshold.
 */
function jobPayload(plan) {
  if (!plan || plan.ok === false) {
    const err = new Error('请先完成同意确认')
    err.code = 'CONSENT_REQUIRED'
    throw err
  }
  const base = {
    consent: true,
    thirdPartyConsent: true,
    consentVersion: limits.CONSENT_VERSION,
    source: plan.source
  }
  if (plan.channel === 'inline') {
    if (plan.bytes > limits.PASTE_INLINE_MAX_BYTES) {
      const err = new Error('文本超过普通提交上限，请改走存储直传')
      err.code = 'OVERSIZE_USE_STORAGE'
      throw err
    }
    return Object.assign({}, base, { text: plan.text })
  }
  if (!plan.uploadId) {
    const err = new Error('缺少直传文件')
    err.code = 'MISSING_UPLOAD'
    throw err
  }
  return Object.assign({}, base, { uploadId: plan.uploadId })
}

module.exports = {
  utf8ByteLength: utf8ByteLength,
  planPaste: planPaste,
  limitLabel: limitLabel,
  buildSubmitPlan: buildSubmitPlan,
  jobPayload: jobPayload,
  extensionOf: extensionOf,
  CONSENT_VERSION: limits.CONSENT_VERSION,
  PASTE_INLINE_MAX_BYTES: limits.PASTE_INLINE_MAX_BYTES,
  FILE_MAX_BYTES: limits.FILE_MAX_BYTES,
  POLL_INTERVAL_MS: limits.POLL_INTERVAL_MS
}
