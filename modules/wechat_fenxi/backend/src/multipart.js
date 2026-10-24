const { fail } = require('./errors')

function parseMultipart(buffer, contentType) {
  const match = /boundary=(?:"([^"]+)"|([^;\s]+))/i.exec(contentType || '')
  if (!match) throw fail(400, 'BAD_MULTIPART', '缺少 multipart boundary')
  const boundary = match[1] || match[2]
  const opener = Buffer.from('--' + boundary)
  if (buffer.indexOf(opener) !== 0) throw fail(400, 'BAD_MULTIPART', 'multipart 格式不正确')
  const delim = Buffer.from('\r\n--' + boundary)
  let pos = opener.length
  const parts = []
  while (pos < buffer.length) {
    if (buffer[pos] === 45 && buffer[pos + 1] === 45) break
    if (buffer[pos] === 13 && buffer[pos + 1] === 10) pos += 2
    else if (buffer[pos] === 10) pos += 1
    else throw fail(400, 'BAD_MULTIPART', 'multipart 分段缺少换行')
    const next = buffer.indexOf(delim, pos)
    const end = next === -1 ? buffer.length : next
    const part = buffer.subarray(pos, end)
    const sep = Buffer.from('\r\n\r\n')
    const headerEnd = part.indexOf(sep)
    if (headerEnd < 0) throw fail(400, 'BAD_MULTIPART', '缺少分段头')
    const headerText = part.subarray(0, headerEnd).toString('utf8')
    const nameMatch = /name="([^"]+)"/i.exec(headerText)
    const fileMatch = /filename="([^"]*)"/i.exec(headerText)
    parts.push({
      name: nameMatch ? nameMatch[1] : '',
      filename: fileMatch ? fileMatch[1] : '',
      data: part.subarray(headerEnd + sep.length)
    })
    if (next === -1) break
    pos = next + delim.length
  }
  return parts
}

module.exports = { parseMultipart }
