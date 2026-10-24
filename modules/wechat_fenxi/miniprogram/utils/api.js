const policy = require('./import-policy')

function apiBase() {
  const app = getApp()
  return (app.globalData && app.globalData.apiBase) || 'http://127.0.0.1:8787'
}

function request(options) {
  const headers = Object.assign({ 'content-type': 'application/json' }, options.header || {})
  const app = getApp()
  if (options.auth !== false && app.globalData.token) {
    headers.Authorization = 'Bearer ' + app.globalData.token
  }
  return new Promise(function (resolve, reject) {
    wx.request({
      url: options.url.indexOf('http') === 0 ? options.url : apiBase() + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: headers,
      success: function (res) {
        const body = res.data || {}
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(body)
          return
        }
        const message = body.error && body.error.message ? body.error.message : '请求失败'
        const err = new Error(message)
        err.code = body.error && body.error.code
        err.statusCode = res.statusCode
        reject(err)
      },
      fail: function (err) {
        reject(err || new Error('网络失败'))
      }
    })
  })
}

function ensureSession() {
  const app = getApp()
  if (app.globalData.token) return Promise.resolve(app.globalData.token)
  return new Promise(function (resolve, reject) {
    wx.login({
      success: function (login) {
        request({
          url: '/api/auth/session',
          method: 'POST',
          data: { code: login.code },
          auth: false
        }).then(function (data) {
          app.globalData.token = data.token
          wx.setStorageSync('token', data.token)
          resolve(data.token)
        }).catch(reject)
      },
      fail: reject
    })
  })
}

function createJob(payload) {
  return request({ url: '/api/jobs', method: 'POST', data: payload })
}

function getJob(id) {
  return request({ url: '/api/jobs/' + id, method: 'GET' })
}

function deleteJob(id) {
  return request({ url: '/api/jobs/' + id, method: 'DELETE' })
}

function deleteAll() {
  return request({ url: '/api/me/data', method: 'DELETE' })
}

/** Direct-to-storage path. The text is not placed in POST /api/jobs. */
function putTextDirect(text) {
  const bytes = policy.utf8ByteLength(text)
  return request({
    url: '/api/storage/presign',
    method: 'POST',
    data: {
      filename: 'paste.txt',
      bytes: bytes,
      source: 'paste',
      consent: true,
      thirdPartyConsent: true,
      consentVersion: policy.CONSENT_VERSION
    }
  }).then(function (presign) {
    return new Promise(function (resolve, reject) {
      wx.request({
        url: presign.url,
        method: 'PUT',
        data: text,
        header: Object.assign({ 'content-type': 'text/plain; charset=utf-8' }, presign.headers || {}),
        success: function (res) {
          if (res.statusCode >= 200 && res.statusCode < 300) resolve(presign.uploadId)
          else reject(new Error('直传失败'))
        },
        fail: reject
      })
    })
  })
}

function uploadChatFile(file) {
  const app = getApp()
  return new Promise(function (resolve, reject) {
    wx.uploadFile({
      url: apiBase() + '/api/uploads',
      filePath: file.path,
      name: 'file',
      header: { Authorization: 'Bearer ' + (app.globalData.token || '') },
      formData: {
        consent: 'true',
        thirdPartyConsent: 'true',
        consentVersion: policy.CONSENT_VERSION
      },
      success: function (res) {
        let body = {}
        try { body = JSON.parse(res.data || '{}') } catch (err) { body = {} }
        if (res.statusCode >= 200 && res.statusCode < 300 && body.uploadId) resolve(body.uploadId)
        else reject(new Error((body.error && body.error.message) || '文件上传失败'))
      },
      fail: reject
    })
  })
}

module.exports = {
  request: request,
  ensureSession: ensureSession,
  createJob: createJob,
  getJob: getJob,
  deleteJob: deleteJob,
  deleteAll: deleteAll,
  putTextDirect: putTextDirect,
  uploadChatFile: uploadChatFile
}
