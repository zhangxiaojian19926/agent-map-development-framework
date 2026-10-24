const { assertSummary } = require('./schema')
const { fail } = require('./errors')

/**
 * LlmProvider surface:
 *   summarizeChunk(messages) -> summary
 *   mergeSummaries(partials, messages) -> summary
 * Default runtime provider is MockLlmProvider (no network, no API key).
 * LLM_PROVIDER=openai plus LLM_API_KEY uses OpenAICompatibleProvider.
 * LLM_PROVIDER=minimax plus MINIMAX_API_KEY uses the same client against
 * MiniMax's OpenAI-compatible chat completions endpoint.
 */
class MockLlmProvider {
  constructor() {
    this.calls = []
  }

  async summarizeChunk(messages) {
    this.calls.push({ op: 'chunk', count: messages.length })
    return summarizeMessages(messages)
  }

  async mergeSummaries(partials, messages) {
    this.calls.push({ op: 'merge', count: partials.length })
    return mergeSummaries(partials, messages)
  }
}

class OpenAICompatibleProvider {
  constructor(options) {
    this.baseUrl = (options.baseUrl || 'https://api.openai.com/v1').replace(/\/$/, '')
    this.apiKey = options.apiKey
    this.model = options.model || 'gpt-4o-mini'
    this.fetchImpl = options.fetchImpl || fetch
    this.jsonObject = options.jsonObject !== false
    this.extraBody = options.extraBody || null
    this.calls = []
  }

  async summarizeChunk(messages) {
    this.calls.push({ op: 'chunk', count: messages.length })
    return this.complete(messages, null)
  }

  async mergeSummaries(partials, messages) {
    this.calls.push({ op: 'merge', count: partials.length })
    return this.complete(messages, partials)
  }

  async complete(messages, partials) {
    const body = {
      model: this.model,
      temperature: 0,
      messages: [
        {
          role: 'system',
          content: '你只根据用户给出的聊天文本做要点摘要。不要编造没有出现的决议。只输出一个 JSON 对象，字段必须是 title, key_points, action_items, decisions, open_questions, participants。action_items 的元素是 {who, what, due}，due 没有就用 null。'
        },
        {
          role: 'user',
          content: JSON.stringify({ messages: messages, partials: partials })
        }
      ]
    }
    if (this.jsonObject) body.response_format = { type: 'json_object' }
    if (this.extraBody) Object.assign(body, this.extraBody)
    const response = await this.fetchImpl(this.baseUrl + '/chat/completions', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        authorization: 'Bearer ' + this.apiKey
      },
      body: JSON.stringify(body)
    })
    if (!response.ok) throw fail(502, 'LLM_UPSTREAM', '摘要服务暂时失败')
    const data = await response.json()
    const message = data && data.choices && data.choices[0] && data.choices[0].message
    const raw = message ? (message.content || '') : ''
    return assertSummary(parseModelJson(stripThink(raw)))
  }
}

class FlakyLlmProvider extends MockLlmProvider {
  constructor(options) {
    super()
    this.failuresLeft = (options && options.failuresLeft) || 1
  }

  async summarizeChunk(messages) {
    this.calls.push({ op: 'chunk', count: messages.length })
    if (this.failuresLeft > 0) {
      this.failuresLeft -= 1
      throw fail(502, 'LLM_UPSTREAM', '临时失败')
    }
    return summarizeMessages(messages)
  }
}

const MINIMAX_BASE_URL = 'https://api.minimax.cn/v1'
const MINIMAX_MODEL = 'MiniMax-M3.1-Flash'

function buildLlmFromEnv(env) {
  const source = env || process.env
  if (source.LLM_PROVIDER === 'minimax' && (source.MINIMAX_API_KEY || source.LLM_API_KEY)) {
    return new OpenAICompatibleProvider({
      apiKey: source.MINIMAX_API_KEY || source.LLM_API_KEY,
      baseUrl: source.MINIMAX_BASE_URL || source.LLM_BASE_URL || MINIMAX_BASE_URL,
      model: source.MINIMAX_MODEL || source.LLM_MODEL || MINIMAX_MODEL,
      jsonObject: false,
      extraBody: { reasoning_effort: 'low', max_completion_tokens: 2048 }
    })
  }
  if (source.LLM_PROVIDER === 'openai' && source.LLM_API_KEY) {
    return new OpenAICompatibleProvider({
      apiKey: source.LLM_API_KEY,
      baseUrl: source.LLM_BASE_URL,
      model: source.LLM_MODEL
    })
  }
  return new MockLlmProvider()
}

function summarizeMessages(messages) {
  const participants = []
  const keyPoints = []
  const actionItems = []
  const decisions = []
  const openQuestions = []
  for (const message of messages || []) {
    const sender = message.sender || '未知'
    if (participants.indexOf(sender) < 0) participants.push(sender)
    const content = String(message.content || '').trim()
    if (!content) continue
    if (keyPoints.length < 8) keyPoints.push(clip(sender + ': ' + content))
    if (/[?？]/.test(content)) openQuestions.push(clip(content))
    if (/决定|敲定|就这么定|达成一致|同意采用/.test(content)) decisions.push(clip(content))
    if (/待办|负责|截止|请.{0,24}(完成|发送|确认|整理|交)/.test(content)) {
      actionItems.push({ who: sender, what: clip(content), due: extractDue(content) })
    }
  }
  if (!keyPoints.length) keyPoints.push('没有提取到要点')
  return {
    title: (participants.slice(0, 3).join('、') || '聊天') + '的要点',
    key_points: keyPoints,
    action_items: actionItems,
    decisions: decisions,
    open_questions: openQuestions,
    participants: participants
  }
}

function mergeSummaries(partials, messages) {
  const base = summarizeMessages(messages)
  const keyPoints = unique(flatten(partials, 'key_points').concat(base.key_points)).slice(0, 12)
  const decisions = unique(flatten(partials, 'decisions').concat(base.decisions)).slice(0, 12)
  const openQuestions = unique(flatten(partials, 'open_questions').concat(base.open_questions)).slice(0, 12)
  const participants = unique(flatten(partials, 'participants').concat(base.participants))
  const actionItems = []
  const seen = new Set()
  partials.concat([base]).forEach(function (part) {
    (part.action_items || []).forEach(function (item) {
      const key = item.who + '\n' + item.what
      if (seen.has(key)) return
      seen.add(key)
      actionItems.push({ who: item.who, what: item.what, due: item.due == null ? null : item.due })
    })
  })
  return {
    title: (partials[0] && partials[0].title) || base.title,
    key_points: keyPoints.length ? keyPoints : base.key_points,
    action_items: actionItems,
    decisions: decisions,
    open_questions: openQuestions,
    participants: participants
  }
}

function flatten(partials, key) {
  const out = []
  for (const part of partials || []) {
    const list = part[key] || []
    for (const item of list) out.push(item)
  }
  return out
}

function unique(list) {
  const out = []
  for (const item of list) {
    if (out.indexOf(item) < 0) out.push(item)
  }
  return out
}

function clip(value) {
  const text = String(value || '').replace(/\s+/g, ' ').trim()
  return text.length > 160 ? text.slice(0, 160) : text
}

function extractDue(content) {
  const date = content.match(/\d{4}-\d{2}-\d{2}/)
  if (date) return date[0]
  const weekday = content.match(/(周[一二三四五六日天]|星期[一二三四五六日天])前/)
  if (weekday) return weekday[0]
  return null
}

function stripThink(raw) {
  return String(raw || '').replace(/<think>[\s\S]*?<\/think>/gi, '').trim()
}

function parseModelJson(raw) {
  const text = String(raw || '').trim()
  try {
    return JSON.parse(text)
  } catch (err) {
    const match = text.match(/\{[\s\S]*\}/)
    if (!match) throw fail(502, 'SCHEMA_INVALID', '模型没有返回 JSON')
    try {
      return JSON.parse(match[0])
    } catch (inner) {
      throw fail(502, 'SCHEMA_INVALID', '模型返回的 JSON 无法解析')
    }
  }
}

module.exports = {
  MockLlmProvider: MockLlmProvider,
  OpenAICompatibleProvider: OpenAICompatibleProvider,
  FlakyLlmProvider: FlakyLlmProvider,
  buildLlmFromEnv: buildLlmFromEnv,
  summarizeMessages: summarizeMessages
}
