import { Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'

export default function AIFloatingButton({ onClick }) {
  return (
    <motion.button
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      onClick={onClick}
      className="fixed bottom-20 right-4 z-[60] w-14 h-14 rounded-full bg-gradient-to-br from-primary to-primary-dark shadow-lg shadow-primary/40 flex items-center justify-center"
      style={{ boxShadow: '0 4px 20px rgba(255, 107, 53, 0.45)' }}
    >
      <Sparkles size={24} className="text-white" />
      {/* Pulse ring */}
      <span className="absolute inset-0 rounded-full border-2 border-primary animate-ping opacity-30" />
    </motion.button>
  )
}
