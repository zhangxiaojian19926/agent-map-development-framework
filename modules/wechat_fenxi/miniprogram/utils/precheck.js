const limits = require('./limits')
const policy = require('./import-policy')

function isAllowedFilename(name) {
  return limits.ALLOWED_EXT.indexOf(policy.extensionOf(name)) >= 0
}

function precheckFile(file) {
  if (!file || !file.name) {
    return { ok: false, code: 'NO_FILE', message: '没有选择文件' }
  }
  if (!isAllowedFilename(file.name)) {
    return { ok: false, code: 'UNSUPPORTED_TYPE', message: '仅支持 txt、json、md。不能选择数据库或其他格式。' }
  }
  const size = Number(file.size || 0)
  if (size <= 0) return { ok: false, code: 'EMPTY_INPUT', message: '文件是空的' }
  if (size > limits.FILE_MAX_BYTES) {
    return { ok: false, code: 'FILE_TOO_LARGE', message: '单个文件不能超过 10MB' }
  }
  return { ok: true }
}

/**
 * wx.chooseMessageFile wrapper.
 * Primary call uses extension without a leading dot (PC requirement).
 * If the platform rejects the filter (known iOS issue) and the user did not cancel,
 * retry with type "all" and keep only txt/json/md.
 */
function chooseMessageFileWithFallback(choose) {
  const primary = { count: 1, type: 'file', extension: ['txt', 'json', 'md'] }
  return Promise.resolve()
    .then(function () { return choose(primary) })
    .then(function (files) { return filterChosen(files, false) })
    .catch(function (err) {
      if (err && (err.cancelled || /cancel/i.test(String(err.errMsg || err.message || '')))) {
        throw err
      }
      return Promise.resolve()
        .then(function () { return choose({ count: 1, type: 'all' }) })
        .then(function (files) { return filterChosen(files, true) })
    })
}

function filterChosen(files, strict) {
  const list = Array.isArray(files) ? files : []
  const ok = list.filter(function (file) { return isAllowedFilename(file && file.name) })
  if (!ok.length) {
    if (!strict && list.length) {
      const err = new Error('仅支持 txt、json、md')
      err.code = 'UNSUPPORTED_TYPE'
      throw err
    }
    const err = new Error('没有可用的 txt、json 或 md 文件')
    err.code = 'UNSUPPORTED_TYPE'
    throw err
  }
  return ok.slice(0, 1)
}

module.exports = {
  isAllowedFilename: isAllowedFilename,
  precheckFile: precheckFile,
  chooseMessageFileWithFallback: chooseMessageFileWithFallback
}
