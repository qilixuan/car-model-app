import { Home, ShoppingBag, PlusCircle, Heart, User, MessageCircle } from "lucide-react"
import { useLocation, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"

const tabs = [
  { path: "/", icon: Home, label: "首页" },
  { path: "/market", icon: ShoppingBag, label: "市场" },
  { path: "/publish", icon: PlusCircle, label: "发布", center: true },
  { path: "/collection", icon: Heart, label: "收藏" },
  { path: "/profile", icon: User, label: "我的" },
]

export default function TabBar() {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white border-t border-gray-100 safe-bottom z-50">
      <div className="flex items-center justify-around h-16">
        {tabs.map(({ path, icon: Icon, label, center }) => {
          const active = location.pathname === path
          if (center) {
            return (
              <div key={path} className="relative -mt-4">
                <motion.div
                  whileTap={{ scale: 0.9 }}
                  onClick={() => navigate(path)}
                  className="w-14 h-14 rounded-full bg-gradient-to-b from-primary to-primary-dark flex items-center justify-center shadow-lg shadow-primary/30 cursor-pointer"
                >
                  <PlusCircle size={28} className="text-white" />
                </motion.div>
              </div>
            )
          }
          return (
            <motion.div
              key={path}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate(path)}
              className="relative flex flex-col items-center gap-0.5 cursor-pointer px-3 py-1"
            >
              {path === "/profile" && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-primary text-white text-xs flex items-center justify-center font-medium">
                  3
                </span>
              )}
              <Icon size={22} className={active ? "text-primary" : "text-text-secondary"} />
              <span className={`text-xs ${active ? "text-primary font-medium" : "text-text-secondary"}`}>
                {label}
              </span>
              {active && (
                <motion.div
                  layoutId="tab-indicator"
                  className="w-1 h-1 rounded-full bg-primary mt-0.5"
                />
              )}
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
