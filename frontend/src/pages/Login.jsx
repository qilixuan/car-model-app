import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { MessageCircle } from 'lucide-react'

export default function Login({ onLogin }) {
  const navigate = useNavigate()
  const [phone, setPhone] = useState("")
  const [agreed, setAgreed] = useState(false)

  const handleLogin = () => {
    if (phone.length === 11 && agreed) {
      onLogin({ name: "藏家小王", phone, avatar: null })
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="flex-1 flex flex-col items-center justify-center px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary/30">
            <span className="text-4xl">🚗</span>
          </div>
          <h1 className="text-3xl font-bold text-secondary">车模星球</h1>
          <p className="text-text-secondary mt-2">收藏每一程</p>
        </motion.div>

        <div className="w-full max-w-xs space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 20 }}
            transition={{ delay: 0.1 }}
          >
            <input
              type="tel"
              placeholder="请输入手机号"
              value={phone}
              onChange={(e) => setPhone(e.target.value.replace(/\D/g, "").slice(0, 11))}
              className="w-full h-12 px-4 rounded-xl border border-gray-200 bg-white text-text-primary placeholder:text-text-secondary focus:outline-none focus:border-primary transition-colors"
            />
          </motion.div>

          <motion.button
            whileTap={{ scale: 0.98 }}
            onClick={handleLogin}
            className="w-full h-12 rounded-xl bg-gradient-to-r from-primary to-primary-dark text-white font-semibold shadow-lg shadow-primary/30 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={phone.length !== 11 || !agreed}
          >
            登录
          </motion.button>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 20 }}
            transition={{ delay: 0.2 }}
            className="relative"
          >
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-background text-text-secondary">其他登录方式</span>
            </div>
          </motion.div>

          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 20 }}
            transition={{ delay: 0.3 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate('/wechat-login')}
            className="w-full h-12 rounded-xl bg-[#07C160] text-white font-semibold flex items-center justify-center gap-2"
          >
            <MessageCircle className="w-5 h-5" /> 微信一键登录
          </motion.button>

          <label className="flex items-center gap-2 justify-center mt-4 cursor-pointer">
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            <span className="text-xs text-text-secondary">
              我已阅读并同意 <span className="text-primary">《用户协议》</span> 和 <span className="text-primary">《隐私政策》</span>
            </span>
          </label>
        </div>
      </div>
    </div>
  )
}
