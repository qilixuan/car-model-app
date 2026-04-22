import { useState } from 'react'
import { motion } from 'framer-motion'
import { MessageCircle, ArrowLeft, Loader2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import useStore from '../store/useStore'

export default function WeChatLogin() {
  const navigate = useNavigate()
  const { setUser, setIsLoggedIn } = useStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleWeChatLogin = async () => {
    setLoading(true)
    setError('')
    
    try {
      // 调用后端微信登录接口
      const response = await fetch('/api/auth/wechat/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      
      const data = await response.json()
      
      if (response.ok) {
        // 微信登录成功
        setUser(data.user)
        setIsLoggedIn(true)
        navigate('/')
      } else {
        setError(data.message || '微信登录失败')
      }
    } catch (err) {
      setError('网络错误，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="flex items-center p-4 bg-surface">
        <button onClick={() => navigate(-1)} className="p-2 -ml-2">
          <ArrowLeft className="w-6 h-6 text-text-primary" />
        </button>
        <span className="flex-1 text-center font-semibold text-text-primary">微信登录</span>
        <div className="w-10" />
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-8">
        {/* App Logo */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="w-24 h-24 bg-primary rounded-3xl flex items-center justify-center mb-8 shadow-lg"
        >
          <span className="text-4xl">🚗</span>
        </motion.div>

        <h1 className="text-2xl font-bold text-text-primary mb-2">车模星球</h1>
        <p className="text-text-secondary mb-12 text-center">汽车模型交易与收藏平台</p>

        {/* WeChat Login Button */}
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={handleWeChatLogin}
          disabled={loading}
          className="w-full max-w-xs bg-[#07C160] text-white py-4 rounded-2xl font-semibold flex items-center justify-center gap-3 shadow-lg disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <MessageCircle className="w-5 h-5" />
          )}
          {loading ? '登录中...' : '微信登录'}
        </motion.button>

        {/* Error */}
        {error && (
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-error text-sm mt-4"
          >
            {error}
          </motion.p>
        )}

        {/* Agreement */}
        <p className="text-text-secondary text-xs mt-8 text-center">
          登录即表示同意<br />
          <span className="text-primary">《用户服务协议》</span> 和 <span className="text-primary">《隐私政策》</span>
        </p>
      </div>
    </div>
  )
}
