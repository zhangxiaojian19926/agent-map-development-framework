App({
  globalData: {
    token: '',
    apiBase: 'http://127.0.0.1:8787'
  },
  onLaunch: function () {
    try {
      const saved = wx.getStorageSync('token')
      if (saved) this.globalData.token = saved
    } catch (err) {
      this.globalData.token = ''
    }
  }
})
