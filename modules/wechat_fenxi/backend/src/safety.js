/**
 * Content safety runs before any LLM call.
 * LocalKeywordSafety is the always-on checker.
 * WeChatMsgSecCheck is the plug-in for wxa/msg_sec_check (version 2).
 * It is not called unless a token provider is configured.
 */

const RULES = [
  { id: 'minor_sexual', re: /儿童色情|幼童色情|未成年人性|未成年.{0,4}色情|童婚卖淫/ },
  { id: 'csam_trade', re: /出售儿童裸|求购儿童裸/ },
  { id: 'weapon_trade', re: /买卖枪支|出售手枪|贩卖枪支/ },
  { id: 'explosive_trade', re: /买卖炸药|出售炸弹/ }
]

class LocalKeywordSafety {
  async check(text) {
    const raw = normalize(text)
    const messages = splitRough(raw)
    for (const piece of messages) {
      const flat = piece.replace(/[^\p{L}\p{N}]+/gu, '')
      for (const rule of RULES) {
        if (rule.re.test(piece) || rule.re.test(flat)) {
          return {
            ok: false,
            provider: 'local-keyword',
            code: 'CONTENT_BLOCKED',
            ruleId: rule.id,
            message: '内容未通过安全检查，未送去生成摘要'
          }
        }
      }
    }
    return { ok: true, provider: 'local-keyword' }
  }
}

class WeChatMsgSecCheck {
  /**
   * @param {{ fetchImpl: Function, getAccessToken: Function }} options
   * Plug into composite safety when the mini program has a real access token.
   * Endpoint: POST https://api.weixin.qq.com/wxa/msg_sec_check?access_token=ACCESS_TOKEN
   * Body (v2): { openid, scene: 2, version: 2, content }
   */
  constructor(options) {
    this.fetchImpl = options.fetchImpl
    this.getAccessToken = options.getAccessToken
  }

  async check(text, ctx) {
    const token = await this.getAccessToken()
    const slices = sliceText(String(text || ''), 2500)
    for (const content of slices) {
      const response = await this.fetchImpl(
        'https://api.weixin.qq.com/wxa/msg_sec_check?access_token=' + encodeURIComponent(token),
        {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({
            openid: (ctx && ctx.openid) || '',
            scene: 2,
            version: 2,
            content: content
          })
        }
      )
      const data = await response.json()
      if (data.errcode && data.errcode !== 0) {
        return {
          ok: false,
          provider: 'wechat-msgSecCheck',
          code: 'MSG_SEC_CHECK_ERROR',
          message: '微信内容安全接口返回错误'
        }
      }
      const suggest = data.result && data.result.suggest
      if (suggest && suggest !== 'pass') {
        return {
          ok: false,
          provider: 'wechat-msgSecCheck',
          code: 'CONTENT_BLOCKED',
          message: '内容未通过微信内容安全检测'
        }
      }
    }
    return { ok: true, provider: 'wechat-msgSecCheck' }
  }
}

class ContentSafetyPipeline {
  constructor(options) {
    this.local = (options && options.local) || new LocalKeywordSafety()
    this.wechat = options && options.wechat ? options.wechat : null
  }

  async check(text, ctx) {
    const local = await this.local.check(text, ctx)
    if (!local.ok) return local
    if (!this.wechat) return { ok: true, provider: 'local-keyword' }
    const remote = await this.wechat.check(text, ctx)
    if (!remote.ok) return remote
    return { ok: true, provider: 'local+wechat-msgSecCheck' }
  }
}

function buildSafetyFromEnv(env) {
  const source = env || process.env
  const local = new LocalKeywordSafety()
  const appid = source.WECHAT_APPID || source.WECHAT_APP_ID
  const secret = source.WECHAT_SECRET || source.WECHAT_APP_SECRET
  const wantWechat = source.CONTENT_SAFETY === 'wechat' || source.CONTENT_SAFETY === 'composite'
  if (!wantWechat || !appid || !secret) {
    return new ContentSafetyPipeline({ local: local })
  }
  const wechat = new WeChatMsgSecCheck({
    fetchImpl: fetch,
    getAccessToken: async function () {
      const url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='
        + encodeURIComponent(appid) + '&secret=' + encodeURIComponent(secret)
      const response = await fetch(url)
      const data = await response.json()
      if (!data.access_token) {
        const err = new Error('微信 access_token 获取失败')
        err.code = 'MSG_SEC_CHECK_ERROR'
        throw err
      }
      return data.access_token
    }
  })
  return new ContentSafetyPipeline({ local: local, wechat: wechat })
}

function normalize(text) {
  return String(text || '').normalize('NFKC').replace(/[\u200b\u200c\u200d\ufeff]/g, '')
}

function splitRough(text) {
  const parts = String(text || '').split(/\n+/)
  return parts.length ? parts : ['']
}

function sliceText(text, size) {
  if (!text) return ['']
  const out = []
  for (let i = 0; i < text.length; i += size) out.push(text.slice(i, i + size))
  return out
}

module.exports = {
  RULES: RULES,
  LocalKeywordSafety: LocalKeywordSafety,
  WeChatMsgSecCheck: WeChatMsgSecCheck,
  ContentSafetyPipeline: ContentSafetyPipeline,
  buildSafetyFromEnv: buildSafetyFromEnv
}
