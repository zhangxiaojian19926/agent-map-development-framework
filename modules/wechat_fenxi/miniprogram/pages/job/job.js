const api = require('../../utils/api')
const policy = require('../../utils/import-policy')

const STATUS = {
  pending: '排队中',
  parsing: '正在整理文本',
  summarizing: '正在生成摘要',
  done: '已完成',
  failed: '没有完成'
}

Page({
  data: {
    status: 'pending',
    statusText: '排队中',
    statusLog: [],
    error: null
  },
  onLoad: function (query) {
    this.jobId = query.id
    this.poll()
    this.timer = setInterval(this.poll.bind(this), policy.POLL_INTERVAL_MS)
  },
  onUnload: function () {
    if (this.timer) clearInterval(this.timer)
  },
  poll: function () {
    const self = this
    if (!this.jobId) return
    api.getJob(this.jobId).then(function (job) {
      self.setData({
        status: job.status,
        statusText: STATUS[job.status] || job.status,
        statusLog: job.statusLog || [],
        error: job.error
      })
      if (job.status === 'done') {
        if (self.timer) clearInterval(self.timer)
        wx.redirectTo({ url: '/pages/result/result?id=' + self.jobId })
      }
      if (job.status === 'failed' && self.timer) clearInterval(self.timer)
    }).catch(function (err) {
      self.setData({
        status: 'failed',
        statusText: '没有完成',
        error: { message: (err && err.message) || '刷新状态失败' }
      })
    })
  },
  back: function () {
    wx.navigateBack({ delta: 1 })
  }
})
