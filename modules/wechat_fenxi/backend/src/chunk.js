function renderMessage(message) {
  const ts = message.ts ? String(message.ts) + ' ' : ''
  return ts + message.sender + ': ' + message.content
}

function chunkMessages(messages, budget) {
  const limit = Math.max(200, Number(budget) || 4000)
  const chunks = []
  let current = []
  let size = 0
  for (const message of messages) {
    const piece = renderMessage(message)
    if (current.length && size + piece.length + 1 > limit) {
      chunks.push(current)
      current = []
      size = 0
    }
    current.push(message)
    size += piece.length + 1
  }
  if (current.length) chunks.push(current)
  return chunks
}

module.exports = { chunkMessages, renderMessage }
