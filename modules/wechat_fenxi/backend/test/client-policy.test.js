const test = require('node:test')
const assert = require('node:assert/strict')
const fs = require('fs')
const path = require('path')
const precheck = require('../../miniprogram/utils/precheck')
const limits = require('../../miniprogram/utils/limits')

const miniRoot = path.join(__dirname, '../../miniprogram')

function readTree(dir) {
  const out = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) out.push.apply(out, readTree(full))
    else if (/\.(js|wxml|json|wxss)$/.test(entry.name)) out.push(full)
  }
  return out
}

test('file precheck and chooseMessageFile fallback', async function () {
  assert.equal(precheck.precheckFile({ name: 'chat.TXT', size: 10 }).ok, true)
  assert.equal(precheck.precheckFile({ name: 'msg.db', size: 10 }).code, 'UNSUPPORTED_TYPE')
  assert.equal(precheck.precheckFile({ name: 'a.exe', size: 10 }).code, 'UNSUPPORTED_TYPE')
  assert.equal(precheck.precheckFile({ name: 'big.txt', size: limits.FILE_MAX_BYTES + 1 }).code, 'FILE_TOO_LARGE')

  const calls = []
  const chosen = await precheck.chooseMessageFileWithFallback(function (spec) {
    calls.push(spec)
    if (spec.type === 'file') {
      const err = new Error('extension filter failed')
      err.errMsg = 'chooseMessageFile:fail'
      throw err
    }
    return [
      { name: 'photo.png', size: 10, path: 'a' },
      { name: 'chat.TXT', size: 20, path: 'b' }
    ]
  })
  assert.equal(calls[0].type, 'file')
  assert.deepEqual(calls[0].extension, ['txt', 'json', 'md'])
  assert.equal(calls[1].type, 'all')
  assert.equal(chosen.length, 1)
  assert.equal(chosen[0].name, 'chat.TXT')

  await assert.rejects(function () {
    return precheck.chooseMessageFileWithFallback(function () {
      const err = new Error('cancel')
      err.errMsg = 'chooseMessageFile:fail cancel'
      throw err
    })
  })
})

test('onboarding copy does not claim chat sync, and the import page gates on consent', function () {
  const files = readTree(miniRoot)
  const text = files.map(function (file) { return fs.readFileSync(file, 'utf8') }).join('\n')
  const claims = text.split(/[。！？\n]/).filter(function (sentence) {
    if (!/自动同步|一键同步|自动读取|读取微信聊天|读取你的微信/.test(sentence)) return false
    return !/不会|不能|不可|不提供|不使用|不要|而非/.test(sentence)
  })
  assert.deepEqual(claims, [])
  assert.match(text, /文件传输助手/)
  assert.match(text, /合并转发/)
  assert.match(text, /不会读取微信里的聊天/)
  assert.match(text, /24 小时/)
  assert.match(text, /chooseMessageFile/)
  assert.match(text, /disabled="\{\{!canSubmit/)
  const importJs = fs.readFileSync(path.join(miniRoot, 'pages/import/import.js'), 'utf8')
  assert.match(importJs, /putTextDirect/)
  assert.match(importJs, /channel === 'inline'/)
  assert.match(importJs, /uploadChatFile/)
  const project = fs.readFileSync(path.join(miniRoot, 'project.config.json'), 'utf8')
  assert.match(project, /miniprogram/)
})

test('backend source does not bundle PC WeChat database decryption', function () {
  const src = path.join(__dirname, '../src')
  const files = readTree(src)
  const text = files.map(function (file) { return fs.readFileSync(file, 'utf8') }).join('\n')
  for (const marker of ['PyWxDump', 'sqlcipher', 'WeChatWin.dll', 'sqlite3_key']) {
    assert.equal(text.includes(marker), false, marker)
  }
  assert.match(text, /msg_sec_check/)
})
