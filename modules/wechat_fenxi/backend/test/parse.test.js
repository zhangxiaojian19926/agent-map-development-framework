const test = require('node:test')
const assert = require('node:assert/strict')
const { parseUpload } = require('../src/parse')
const { decodeBytes } = require('../src/encoding')
const { GBK_TXT_HEX, GBK_JSON_HEX, GBK_MD_HEX } = require('./helpers')

test('UTF-8 TXT lines with and without a timestamp', function () {
  const parsed = parseUpload({
    filename: 'chat.txt',
    text: [
      '2026-01-02 09:30:00 张三: 会议改到三点',
      '李四: 我来记',
      '第二行还是李四说的'
    ].join('\n')
  })
  assert.equal(parsed.format, 'txt')
  assert.equal(parsed.messages.length, 2)
  assert.equal(parsed.messages[0].sender, '张三')
  assert.equal(parsed.messages[0].ts, '2026-01-02 09:30:00')
  assert.equal(parsed.messages[1].sender, '李四')
  assert.match(parsed.messages[1].content, /第二行还是李四说的/)
})

test('UTF-8 wechat-chat-export TXT keeps media notes on the same message', function () {
  const text = [
    'WeChat Chat Export for LLM v1.3.5',
    '会话类型：私聊',
    '会话名称：张三',
    '消息总数：2',
    '='.repeat(70),
    '',
    '========== 2026-01-02 ==========',
    '',
    '2026-01-02 09:30:00 | 张三：会议改到三点，请李四周五前交纪要',
    '    ↳ 图片：media/images/a.jpg',
    '2026-01-02 09:31:00 | 李四：就这么定了？'
  ].join('\n')
  const parsed = parseUpload({ filename: 'chat_full_for_llm.txt', text: text })
  assert.equal(parsed.messages.length, 2)
  assert.equal(parsed.messages[0].sender, '张三')
  assert.match(parsed.messages[0].content, /图片/)
  assert.equal(parsed.messages[1].sender, '李四')
  assert.equal(parsed.messages.some(function (m) { return m.sender === '会话类型' }), false)
})

test('UTF-8 JSON array and {messages} including wechat-chat-export fields', function () {
  const arrayParsed = parseUpload({
    filename: 'a.json',
    text: JSON.stringify([
      { from: '张三', timestamp: '2026-01-02 09:30:00', text: '你好' }
    ])
  })
  assert.equal(arrayParsed.messages[0].sender, '张三')
  assert.equal(arrayParsed.messages[0].content, '你好')

  const exportParsed = parseUpload({
    filename: 'chat_full_parsed.json',
    text: JSON.stringify({
      exporter_version: '1.3.5',
      chat_name: '张三',
      messages: [
        { sender: '张三', time: '2026-01-02 09:30:00', content: '会议改到三点', type: '文本' },
        { role: '李四', content: '收到' }
      ]
    })
  })
  assert.equal(exportParsed.format, 'json')
  assert.equal(exportParsed.messages.length, 2)
  assert.equal(exportParsed.messages[1].sender, '李四')
})

test('UTF-8 Markdown export and plain markdown', function () {
  const exported = [
    '# 张三',
    '',
    '- 导出器：WeChat Chat Export for LLM v1.3.5',
    '- 会话类型：私聊',
    '',
    '## 2026-01-02',
    '',
    '**09:30:00 | 张三：** 会议改到三点，请李四周五前交纪要',
    '',
    '**09:31:00 | 李四：** 就这么定了？'
  ].join('\n')
  const parsed = parseUpload({ filename: 'chat_full_for_llm.md', text: exported })
  assert.equal(parsed.format, 'md')
  assert.equal(parsed.messages.length, 2)
  assert.equal(parsed.messages[0].ts, '2026-01-02 09:30:00')
  assert.equal(parsed.messages[0].sender, '张三')

  const plain = parseUpload({
    filename: 'notes.md',
    text: '---\ntitle: memo\n---\n\n# 备忘\n\n明天下午记得把纪要发给大家。\n'
  })
  assert.equal(plain.format, 'md')
  assert.equal(plain.messages.length, 1)
  assert.match(plain.messages[0].content, /纪要/)
})

test('GBK TXT, JSON, and MD decode before parse', function () {
  const txt = decodeBytes(Buffer.from(GBK_TXT_HEX, 'hex'))
  assert.equal(txt.encoding, 'gbk')
  const txtParsed = parseUpload({ filename: 'gbk.txt', text: txt.text })
  assert.deepEqual(txtParsed.messages.map(function (m) { return m.sender }), ['张三', '李四'])
  assert.match(txtParsed.messages[0].content, /会议改到三点/)

  const json = decodeBytes(Buffer.from(GBK_JSON_HEX, 'hex'))
  assert.equal(json.encoding, 'gbk')
  const jsonParsed = parseUpload({ filename: 'gbk.json', text: json.text })
  assert.equal(jsonParsed.messages[0].sender, '张三')
  assert.match(jsonParsed.messages[1].content, /就这么定了？/)

  const md = decodeBytes(Buffer.from(GBK_MD_HEX, 'hex'))
  assert.equal(md.encoding, 'gbk')
  const mdParsed = parseUpload({ filename: 'gbk.md', text: md.text })
  assert.equal(mdParsed.messages.length, 2)
  assert.equal(mdParsed.messages[1].sender, '李四')
})

test('UTF-8 Chinese is not mislabeled as GBK', function () {
  const decoded = decodeBytes(Buffer.from('张三: 你好', 'utf8'))
  assert.equal(decoded.encoding, 'utf-8')
  assert.equal(decoded.text, '张三: 你好')
})

test('empty string and whitespace are EMPTY_INPUT', function () {
  assert.throws(function () { parseUpload({ text: '   \n\t' }) }, function (err) {
    return err.code === 'EMPTY_INPUT'
  })
  assert.throws(function () { parseUpload({ filename: 'a.json', text: '{"messages":[]}' }) }, function (err) {
    return err.code === 'EMPTY_INPUT'
  })
  assert.throws(function () { parseUpload({ filename: 'a.json', text: '[]' }) }, function (err) {
    return err.code === 'EMPTY_INPUT'
  })
})

test('garbage and broken JSON do not become a fake transcript', function () {
  assert.throws(function () { parseUpload({ filename: 'a.txt', text: '@@@###$$$' }) }, function (err) {
    return err.code === 'UNRECOGNIZED_INPUT'
  })
  assert.throws(function () { parseUpload({ filename: 'a.json', text: '{not json' }) }, function (err) {
    return err.code === 'INVALID_JSON'
  })
  assert.throws(function () { parseUpload({ filename: 'msg.db', text: 'hello world' }) }, function (err) {
    return err.code === 'UNSUPPORTED_TYPE'
  })
})

test('merged-forward bubble stays one unparsed message', function () {
  const xml = '<msg><appmsg><type>19</type><title>群聊的聊天记录</title><des>张三: 你好\n李四: 再见</des></appmsg></msg>'
  const parsed = parseUpload({ filename: 'forward.txt', text: xml })
  assert.equal(parsed.messages.length, 1)
  assert.equal(parsed.messages[0].type, 'merged_forward_unparsed')
  assert.match(parsed.messages[0].content, /type>\s*19/)

  const json = parseUpload({
    filename: 'forward.json',
    text: JSON.stringify({
      messages: [{
        sender: '张三',
        type: '合并转发',
        content: '群聊的聊天记录',
        children: [
          { sender: '李四', content: '不应该被拆出来' },
          { sender: '王五', content: '第二条' }
        ]
      }]
    })
  })
  assert.equal(json.messages.length, 1)
  assert.equal(json.messages[0].type, 'merged_forward_unparsed')
  assert.equal(json.messages[0].content, '群聊的聊天记录')
})
