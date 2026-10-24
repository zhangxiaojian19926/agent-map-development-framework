const limits = require('../../utils/limits')

Page({
  data: { version: limits.CONSENT_VERSION },
  back: function () {
    wx.navigateBack({ delta: 1 })
  }
})
