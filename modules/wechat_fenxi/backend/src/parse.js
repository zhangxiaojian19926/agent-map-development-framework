const { fail } = require('./errors')

const EXPORT_LINE = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| ([^：\n]{1,80})：(.*)$/
const TIME_LINE = /^(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})\s+([^:：\n]{1,80}?)\s*[:：]\s*(.*)$/
const SIMPLE_LINE = /^([^:：\n]{1,40}?)\s*[:：]\s*(\S.*)$/
const MD_LINE = /^\*\*(\d{2}:\d{2}:\d{2})\s*\|\s*([^*]+?)：\*\*\s*(.*)$/
const MD_DATE = /^##\s+(\d{4}-\d{2}-\d{2})\s*$/

/**
 * Normalize uploaded/pasted chat text into messages[].
 * Merged-forward bubbles (appmsg type 19, or a JSON children/forward list)
 * stay a single unparsed message. This module does not decrypt anything.
 */
function parseUpload(input) {
  const text = String((input && input.text) || '').replace(/^\uFEFF/, '')
  const filename = String((input && input.filename) || '')
  const ext = extensionOf(filename)
  if (ext && ['txt', 'json', 'md', 'markdown'].indexOf(ext) < 0) {
    throw fail(400, 'UNSUPPORTED_TYPE', '仅支持 txt、json、md 文本')
  }
  if (!text.trim()) throw fail(400, 'EMPTY_INPUT', '没有可读内容')

  if (ext === 'json' || (ext !== 'md' && ext !== 'markdown' && looksLikeJson(text))) {
    try {
      return finish('json', parseJsonMessages(text), text)
    } catch (err) {
      if (ext === 'json' || (err && err.code === 'INVALID_JSON')) throw err
    }
  }

  if (ext === 'md' || ext === 'markdown' || looksLikeWechatMd(text)) {
    const body = stripFrontMatter(text)
    const mdMessages = parseWechatMarkdown(body)
    if (mdMessages.length) return finish('md', mdMessages, text)
    if (ext === 'md' || ext === 'markdown') {
      return finish('md', parseLooseText(body), text)
    }
  }

  return finish('txt', parseLooseText(text), text)
}

function finish(format, messages, raw) {
  const cleaned = []
  for (const message of messages || []) {
    const content = String(message.content || '').trim()
    if (!content) continue
    cleaned.push({
      ts: message.ts || null,
      sender: String(message.sender || '未知').trim() || '未知',
      content: content,
      type: message.type || 'text'
    })
  }
  if (cleaned.length) return { format: format, messages: cleaned }
  if (!String(raw || '').trim()) throw fail(400, 'EMPTY_INPUT', '没有可读内容')
  if (!hasReadableTokens(raw)) {
    throw fail(400, 'UNRECOGNIZED_INPUT', '内容不像聊天文本，也没有可摘要的段落')
  }
  throw fail(400, 'UNRECOGNIZED_INPUT', '没能识别出聊天文本。请使用「时间 昵称: 正文」、JSON 消息数组，或直接粘贴对话段落。')
}

function parseJsonMessages(text) {
  let data
  try {
    data = JSON.parse(String(text).replace(/^\uFEFF/, ''))
  } catch (err) {
    throw fail(400, 'INVALID_JSON', 'JSON 无法解析')
  }
  let list = null
  if (Array.isArray(data)) list = data
  else if (data && Array.isArray(data.messages)) list = data.messages
  else if (data && Array.isArray(data.data)) list = data.data
  else throw fail(400, 'INVALID_JSON', 'JSON 需要是消息数组，或包含 messages 数组')
  const out = []
  for (const item of list) {
    const mapped = mapJsonMessage(item)
    if (mapped) out.push(mapped)
  }
  if (!out.length) throw fail(400, 'EMPTY_INPUT', '没有可读内容')
  return out
}

function mapJsonMessage(item) {
  if (!item || typeof item !== 'object' || Array.isArray(item)) return null
  const typeLabel = String(item.type || item.msg_type || item.msgType || '')
  const merged = isMergedForwardJson(item, typeLabel)
  const content = firstString(item, ['content', 'text', 'message', 'msg', 'body'])
  if (merged) {
    return {
      ts: pickTime(item),
      sender: pickSender(item),
      content: content || '[合并转发聊天记录：这里不把它拆成多条消息。请改为复制文字，或导入已经整理好的 txt / json / md。]',
      type: 'merged_forward_unparsed'
    }
  }
  if (!content) return null
  return {
    ts: pickTime(item),
    sender: pickSender(item),
    content: content,
    type: typeLabel || 'text'
  }
}

function isMergedForwardJson(item, typeLabel) {
  if (/合并转发|chatrecord|forwarded_messages/i.test(typeLabel)) return true
  if (Array.isArray(item.children) || Array.isArray(item.forward_messages) || Array.isArray(item.records)) {
    return true
  }
  return false
}

function parseLooseText(text) {
  if (isMergedForwardXml(text) && !EXPORT_LINE.test(text) && !hasChatLines(text)) {
    return [{
      ts: null,
      sender: '用户粘贴',
      content: text.trim(),
      type: 'merged_forward_unparsed'
    }]
  }
  if (isWechatExportTxt(text)) return parseWechatExportTxt(text)
  const messages = []
  const lines = String(text).split(/\r?\n/)
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue
    if (isSkippableDecoration(trimmed)) continue
    const parsed = parseMessageLine(trimmed)
    if (parsed) {
      messages.push(parsed)
      continue
    }
    if (messages.length && !isMetadataLine(trimmed)) {
      messages[messages.length - 1].content += '\n' + trimmed
      continue
    }
  }
  if (messages.length) return messages
  if (isMergedForwardXml(text)) {
    return [{
      ts: null,
      sender: '用户粘贴',
      content: text.trim(),
      type: 'merged_forward_unparsed'
    }]
  }
  if (isSubstantialProse(text)) {
    return [{
      ts: null,
      sender: '用户粘贴',
      content: text.trim(),
      type: 'text'
    }]
  }
  return []
}

function parseWechatExportTxt(text) {
  const messages = []
  const lines = String(text).split(/\r?\n/)
  for (const line of lines) {
    const match = line.match(EXPORT_LINE)
    if (match) {
      messages.push({ ts: match[1], sender: match[2].trim(), content: match[3], type: 'text' })
      continue
    }
    if (!messages.length) continue
    const trimmed = line.trim()
    if (!trimmed) continue
    if (/^={5,}/.test(trimmed)) continue
    messages[messages.length - 1].content += '\n' + trimmed
  }
  return messages
}

function parseWechatMarkdown(text) {
  const messages = []
  let date = ''
  const lines = String(text).split(/\r?\n/)
  for (const line of lines) {
    const trimmed = line.trim()
    const dateMatch = trimmed.match(MD_DATE)
    if (dateMatch) {
      date = dateMatch[1]
      continue
    }
    const match = trimmed.match(MD_LINE)
    if (!match) continue
    messages.push({
      ts: date ? date + ' ' + match[1] : match[1],
      sender: match[2].trim(),
      content: match[3],
      type: 'text'
    })
  }
  return messages
}

function parseMessageLine(line) {
  let match = line.match(EXPORT_LINE)
  if (match) {
    return { ts: match[1], sender: match[2].trim(), content: match[3], type: 'text' }
  }
  match = line.match(TIME_LINE)
  if (match) {
    return { ts: match[1].replace('T', ' '), sender: match[2].trim(), content: match[3], type: 'text' }
  }
  if (isMetadataLine(line)) return null
  match = line.match(SIMPLE_LINE)
  if (match && !/^https?$/i.test(match[1])) {
    return { ts: null, sender: match[1].trim(), content: match[2], type: 'text' }
  }
  return null
}

function isWechatExportTxt(text) {
  return /WeChat Chat Export for LLM/.test(text) && /会话名称：/.test(text)
}

function looksLikeWechatMd(text) {
  return /导出器：WeChat Chat Export/.test(text) || /^\*\*\d{2}:\d{2}:\d{2}\s*\|/m.test(text)
}

function looksLikeJson(text) {
  const trimmed = text.trim()
  return trimmed.startsWith('{') || trimmed.startsWith('[')
}

function isMergedForwardXml(text) {
  return /<appmsg>/i.test(text) && /<type>\s*19\s*<\/type>/i.test(text)
}

function hasChatLines(text) {
  return EXPORT_LINE.test(text) || TIME_LINE.test(text)
}

function isSkippableDecoration(line) {
  return /^=+$/.test(line) || /^={5,} .* ={5,}$/.test(line)
}

function isMetadataLine(line) {
  return /^(WeChat Chat Export|会话类型|会话名称|消息总数|导出器|聊天记录导出)[:：]/.test(line)
}

function isSubstantialProse(text) {
  const trimmed = String(text || '').trim()
  if (trimmed.length < 4) return false
  if (!hasReadableTokens(trimmed)) return false
  const readable = trimmed.match(/[\p{L}\p{N}]/gu) || []
  return readable.length >= 4
}

function hasReadableTokens(text) {
  return /[\p{L}\p{N}]/u.test(String(text || ''))
}

function stripFrontMatter(text) {
  if (!String(text).startsWith('---\n') && !String(text).startsWith('---\r\n')) return text
  const match = String(text).match(/^---\r?\n[\s\S]*?\r?\n---\r?\n/)
  return match ? text.slice(match[0].length) : text
}

function pickSender(item) {
  const value = firstString(item, ['sender', 'from', 'nickname', 'nick', 'name', 'role', 'user'])
  return value || '未知'
}

function pickTime(item) {
  const value = firstString(item, ['time', 'timestamp', 'ts', 'datetime', 'create_time', 'createTime'])
  return value || null
}

function firstString(item, keys) {
  for (const key of keys) {
    const value = item[key]
    if (typeof value === 'string' && value.trim()) return value.trim()
    if (typeof value === 'number' && Number.isFinite(value)) return String(value)
  }
  return ''
}

function extensionOf(name) {
  const base = String(name || '').split(/[/\\]/).pop()
  const dot = base.lastIndexOf('.')
  if (dot <= 0) return ''
  return base.slice(dot + 1).toLowerCase()
}

module.exports = {
  parseUpload: parseUpload,
  extensionOf: extensionOf
}
