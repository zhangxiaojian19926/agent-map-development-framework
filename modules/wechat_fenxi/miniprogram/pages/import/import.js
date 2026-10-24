const policy = require('../../utils/import-policy')
const precheck = require('../../utils/precheck')
const api = require('../../utils/api')

Page({
  data: {
    tab: 'paste',
    text: '',
    byteSize: 0,
    oversize: false,
    consent: false,
    thirdPartyConsent: false,
    file: null,
    fileError: '',
    submitting: false,
    canSubmit: false,
    limitLabel: policy.limitLabel()
  },
  onTab: function (event) {
    this.setData({ tab: event.currentTarget.dataset.tab })
    this.refreshGate()
  },
  onText: function (event) {
    const text = event.detail.value || ''
    const planned = policy.planPaste(text)
    this.setData({
      text: text,
      byteSize: planned.bytes,
      oversize: planned.channel === 'storage'
    })
    this.refreshGate()
  },
  onConsent: function (event) {
    const values = event.detail.value || []
    this.setData({ consent: values.indexOf('privacy') >= 0 })
    this.refreshGate()
  },
  onThird: function (event) {
    const values = event.detail.value || []
    this.setData({ thirdPartyConsent: values.indexOf('third') >= 0 })
    this.refreshGate()
  },
  refreshGate: function () {
    const plan = policy.buildSubmitPlan({
      mode: this.data.tab,
      text: this.data.text,
      file: this.data.file,
      consent: this.data.consent,
      thirdPartyConsent: this.data.thirdPartyConsent
    })
    this.setData({ canSubmit: !!plan.ok })
  },
  onChooseFile: function () {
    const self = this
    precheck.chooseMessageFileWithFallback(function (spec) {
      return wxChoose(spec)
    }).then(function (files) {
      const file = files[0]
      const checked = precheck.precheckFile(file)
      if (!checked.ok) {
        self.setData({ file: null, fileError: checked.message })
        self.refreshGate()
        return
      }
      self.setData({ file: file, fileError: '' })
      self.refreshGate()
    }).catch(function (err) {
      if (err && (err.cancelled || /cancel/i.test(String(err.errMsg || '')))) return
      self.setData({ fileError: (err && err.message) || '没有选到可用文件' })
    })
  },
  onSubmit: function () {
    const self = this
    const plan = policy.buildSubmitPlan({
      mode: this.data.tab,
      text: this.data.text,
      file: this.data.file,
      consent: this.data.consent,
      thirdPartyConsent: this.data.thirdPartyConsent
    })
    if (!plan.ok) {
      wx.showToast({ title: plan.message, icon: 'none' })
      return
    }
    this.setData({ submitting: true })
    api.ensureSession().then(function () {
      if (plan.channel === 'storage') return api.putTextDirect(plan.text)
      if (plan.channel === 'file') return api.uploadChatFile(plan.file)
      return null
    }).then(function (uploadId) {
      if (uploadId) plan.uploadId = uploadId
      if (plan.channel === 'inline') {
        return api.createJob(policy.jobPayload(plan))
      }
      return api.createJob(policy.jobPayload(plan))
    }).then(function (job) {
      wx.navigateTo({ url: '/pages/job/job?id=' + job.id })
    }).catch(function (err) {
      wx.showToast({ title: (err && err.message) || '提交失败', icon: 'none' })
    }).then(function () {
      self.setData({ submitting: false })
    })
  }
})

function wxChoose(spec) {
  return new Promise(function (resolve, reject) {
    wx.chooseMessageFile({
      count: spec.count,
      type: spec.type,
      extension: spec.extension,
      success: function (res) { resolve(res.tempFiles || []) },
      fail: function (err) { reject(err) }
    })
  })
}
