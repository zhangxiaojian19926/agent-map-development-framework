const { fail } = require('./errors')

function assertSummary(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw fail(502, 'SCHEMA_INVALID', '摘要结果不是 JSON 对象')
  }
  if (typeof value.title !== 'string' || !value.title.trim()) {
    throw fail(502, 'SCHEMA_INVALID', '摘要缺少 title')
  }
  assertStringList(value.key_points, 'key_points')
  assertStringList(value.decisions, 'decisions')
  assertStringList(value.open_questions, 'open_questions')
  assertStringList(value.participants, 'participants')
  if (!Array.isArray(value.action_items)) {
    throw fail(502, 'SCHEMA_INVALID', '摘要缺少 action_items')
  }
  value.action_items.forEach(function (item, index) {
    if (!item || typeof item !== 'object') {
      throw fail(502, 'SCHEMA_INVALID', 'action_items[' + index + '] 无效')
    }
    if (typeof item.who !== 'string' || typeof item.what !== 'string') {
      throw fail(502, 'SCHEMA_INVALID', 'action_items[' + index + '] 缺少 who/what')
    }
    if (!(item.due === null || typeof item.due === 'string')) {
      throw fail(502, 'SCHEMA_INVALID', 'action_items[' + index + '].due 必须是字符串或 null')
    }
  })
  return {
    title: value.title.trim(),
    key_points: value.key_points.map(function (item) { return String(item) }),
    action_items: value.action_items.map(function (item) {
      return {
        who: item.who,
        what: item.what,
        due: item.due === undefined ? null : item.due
      }
    }),
    decisions: value.decisions.map(function (item) { return String(item) }),
    open_questions: value.open_questions.map(function (item) { return String(item) }),
    participants: value.participants.map(function (item) { return String(item) })
  }
}

function assertStringList(value, name) {
  if (!Array.isArray(value) || value.some(function (item) { return typeof item !== 'string' })) {
    throw fail(502, 'SCHEMA_INVALID', '摘要字段 ' + name + ' 必须是字符串数组')
  }
}

module.exports = { assertSummary }
