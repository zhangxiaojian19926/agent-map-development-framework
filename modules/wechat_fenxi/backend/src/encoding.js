/**
 * Detect UTF-8 vs GBK/GB18030.
 * Chinese desktop exports are often GBK. Invalid UTF-8 falls back to GB18030.
 * Node ICU exposes gb18030 via TextDecoder (verified on Node 22).
 */
function decodeBytes(input) {
  const buf = Buffer.isBuffer(input) ? input : Buffer.from(input)
  if (buf.length === 0) return { encoding: 'utf-8', text: '' }

  let encoding = 'utf-8'
  let text
  if (buf.length >= 3 && buf[0] === 0xef && buf[1] === 0xbb && buf[2] === 0xbf) {
    text = decodeUtf8Fatal(buf.subarray(3))
    encoding = 'utf-8'
  } else {
    try {
      text = decodeUtf8Fatal(buf)
      encoding = 'utf-8'
    } catch (err) {
      text = new TextDecoder('gb18030').decode(buf)
      encoding = 'gbk'
    }
  }
  if (text.charCodeAt(0) === 0xfeff) text = text.slice(1)
  const replacement = countChar(text, '\uFFFD')
  if (text.length > 0 && replacement / text.length > 0.05) {
    const err = new Error('无法识别的文本编码')
    err.status = 400
    err.code = 'BAD_ENCODING'
    throw err
  }
  return { encoding: encoding, text: text }
}

function decodeUtf8Fatal(buf) {
  return new TextDecoder('utf-8', { fatal: true }).decode(buf)
}

function countChar(text, ch) {
  let n = 0
  for (let i = 0; i < text.length; i++) if (text[i] === ch) n += 1
  return n
}

module.exports = { decodeBytes }
