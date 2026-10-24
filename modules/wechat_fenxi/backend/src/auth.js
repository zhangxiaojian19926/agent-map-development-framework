const crypto = require('crypto')
const { fail } = require('./errors')

class MockSessionExchanger {
  async exchange(code) {
    if (!code || typeof code !== 'string') throw fail(400, 'INVALID_CODE', '缺少登录 code')
    const openid = crypto.createHash('sha256').update('mock:' + code).digest('hex').slice(0, 28)
    return { openid: openid, sessionKey: 'mock' }
  }
}

class WeChatSessionExchanger {
  constructor(options) {
    this.appid = options.appid
    this.secret = options.secret
    this.fetchImpl = options.fetchImpl || fetch
  }

  async exchange(code) {
    if (!code) throw fail(400, 'INVALID_CODE', '缺少登录 code')
    const url = 'https://api.weixin.qq.com/sns/jscode2session?appid='
      + encodeURIComponent(this.appid)
      + '&secret=' + encodeURIComponent(this.secret)
      + '&js_code=' + encodeURIComponent(code)
      + '&grant_type=authorization_code'
    const response = await this.fetchImpl(url)
    const data = await response.json()
    if (!data.openid) throw fail(401, 'WECHAT_LOGIN_FAILED', '微信登录没有返回 openid')
    return { openid: data.openid, sessionKey: data.session_key || '' }
  }
}

function wechatAppId(source) {
  return source.WECHAT_APPID || source.WECHAT_APP_ID || ''
}

function wechatSecret(source) {
  return source.WECHAT_SECRET || source.WECHAT_APP_SECRET || ''
}

function buildSessionExchanger(env) {
  const source = env || process.env
  const appid = wechatAppId(source)
  const secret = wechatSecret(source)
  if (appid && secret) {
    return new WeChatSessionExchanger({
      appid: appid,
      secret: secret
    })
  }
  return new MockSessionExchanger()
}

function createTokenStore(now) {
  const tokens = new Map()
  return {
    issue: function (openid) {
      const token = crypto.randomBytes(24).toString('hex')
      tokens.set(token, { openid: openid, exp: now() + 7 * 24 * 60 * 60 * 1000 })
      return token
    },
    read: function (token) {
      const row = tokens.get(token)
      if (!row) return null
      if (row.exp <= now()) {
        tokens.delete(token)
        return null
      }
      return row
    },
    deleteUser: function (openid) {
      for (const [token, row] of tokens) {
        if (row.openid === openid) tokens.delete(token)
      }
    }
  }
}

module.exports = {
  MockSessionExchanger: MockSessionExchanger,
  WeChatSessionExchanger: WeChatSessionExchanger,
  buildSessionExchanger: buildSessionExchanger,
  createTokenStore: createTokenStore
}
