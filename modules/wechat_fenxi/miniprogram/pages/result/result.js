const api = require('../../utils/api')

Page({
  data: {
    title: '摘要',
    participants: '',
    keyPoints: [],
    actionItems: [],
    decisions: [],
    openQuestions: []
  },
  onLoad: function (query) {
    this.jobId = query.id
    this.load()
  },
  load: function () {
    const self = this
    api.getJob(this.jobId).then(function (job) {
      if (job.status !== 'done') {
        wx.redirectTo({ url: '/pages/job/job?id=' + self.jobId })
        return
      }
      const result = job.result || {}
      self.summary = result
      self.setData({
        title: result.title || '摘要',
        participants: (result.participants || []).join('、'),
        keyPoints: result.key_points || [],
        actionItems: result.action_items || [],
        decisions: result.decisions || [],
        openQuestions: result.open_questions || []
      })
    }).catch(function (err) {
      wx.showToast({ title: (err && err.message) || '读取结果失败', icon: 'none' })
    })
  },
  copySummary: function () {
    const text = formatSummary(this.summary || {})
    wx.setClipboardData({ data: text })
  },
  removeThis: function () {
    const self = this
    wx.showModal({
      title: '删除这一次分析',
      content: '将删除这次的原文和摘要。',
      success: function (res) {
        if (!res.confirm) return
        api.deleteJob(self.jobId).then(function () {
          wx.redirectTo({ url: '/pages/import/import' })
        }).catch(function (err) {
          wx.showToast({ title: (err && err.message) || '删除失败', icon: 'none' })
        })
      }
    })
  },
  removeAll: function () {
    wx.showModal({
      title: '删除我的数据',
      content: '将删除这个账号在服务器上的原文和摘要，删除后无法恢复。',
      success: function (res) {
        if (!res.confirm) return
        api.deleteAll().then(function () {
          wx.showToast({ title: '已删除', icon: 'none' })
          wx.redirectTo({ url: '/pages/import/import' })
        }).catch(function (err) {
          wx.showToast({ title: (err && err.message) || '删除失败', icon: 'none' })
        })
      }
    })
  }
})

function formatSummary(summary) {
  const lines = [summary.title || '摘要', '']
  lines.push('要点')
  ;(summary.key_points || []).forEach(function (item) { lines.push('- ' + item) })
  lines.push('', '待办')
  ;(summary.action_items || []).forEach(function (item) {
    lines.push('- ' + item.who + '：' + item.what + (item.due ? '（' + item.due + '）' : ''))
  })
  lines.push('', '决策')
  ;(summary.decisions || []).forEach(function (item) { lines.push('- ' + item) })
  lines.push('', '开放问题')
  ;(summary.open_questions || []).forEach(function (item) { lines.push('- ' + item) })
  return lines.join('\n')
}
