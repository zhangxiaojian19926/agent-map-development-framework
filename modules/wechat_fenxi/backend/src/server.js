const fs = require('fs')
const path = require('path')
const { createApp } = require('./create-app')

/**
 * Local API for scheme A.
 * Default LLM is the deterministic mock. Set LLM_PROVIDER=openai and LLM_API_KEY
 * for a generic OpenAI-compatible model, or LLM_PROVIDER=minimax and
 * MINIMAX_API_KEY for MiniMax. WeChat msgSecCheck is off unless
 * CONTENT_SAFETY=composite (or wechat) and WECHAT_APPID / WECHAT_SECRET are set.
 * Values are read from the process environment, then from backend/.env.
 */
function loadEnvFile() {
  const filePath = path.join(__dirname, '..', '.env')
  let text
  try {
    text = fs.readFileSync(filePath, 'utf8')
  } catch (err) {
    if (err && err.code === 'ENOENT') return
    throw err
  }
  const lines = text.split('\n')
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.charAt(0) === '#') continue
    const eq = trimmed.indexOf('=')
    if (eq <= 0) continue
    const key = trimmed.slice(0, eq).trim()
    if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(key)) continue
    let value = trimmed.slice(eq + 1).trim()
    if (value.length >= 2) {
      const quote = value.charAt(0)
      if ((quote === '"' || quote === "'") && value.charAt(value.length - 1) === quote) {
        value = value.slice(1, -1)
      }
    }
    if (process.env[key] == null || process.env[key] === '') process.env[key] = value
  }
}

function main() {
  loadEnvFile()
  const app = createApp({ env: process.env })
  const port = Number(process.env.PORT || 8787)
  app.server.listen(port, '127.0.0.1', function () {
    console.log('scheme A API listening on http://127.0.0.1:' + port)
  })
}

if (require.main === module) main()

module.exports = { main }
