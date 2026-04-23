import { BrowserRouter, Routes, Route } from "react-router-dom"
import { useState } from "react"
import TabBar from "./components/TabBar"
import Home from "./pages/Home"
import AIChatPanel from "./components/AIChatPanel"
import AIFloatingButton from "./components/AIFloatingButton"
import Market from "./pages/Market"
import Publish from "./pages/Publish"
import Collection from "./pages/Collection"
import Profile from "./pages/Profile"
import ProductDetail from "./pages/ProductDetail"
import Login from "./pages/Login"
import ChatList from "./pages/ChatList"
import ChatRoom from "./pages/ChatRoom"
import PriceTrend from "./pages/PriceTrend"
import WeChatLogin from "./pages/WeChatLogin"
import "./index.css"

function App() {
  const [user, setUser] = useState({ id: 1, name: "藏家小王", avatar: null, phone: "139****9923", rating: 4.8 })
  const [showAI, setShowAI] = useState(false)

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background max-w-md mx-auto relative">
        {/* 星仔 AI 悬浮按钮 — 全局显示 */}
        <AIFloatingButton onClick={() => setShowAI(true)} />

        {/* 星仔 AI 聊天面板 */}
        <AIChatPanel open={showAI} onClose={() => setShowAI(false)} />

        <Routes>
          <Route path="/login" element={<Login onLogin={setUser} />} />
          <Route path="/product/:id" element={<ProductDetail user={user} />} />
          <Route path="/chat-list" element={<ChatList />} />
          <Route path="/chat/:id" element={<ChatRoom />} />
          <Route path="/trend" element={<PriceTrend />} />
          <Route path="/wechat-login" element={<WeChatLogin />} />
          <Route path="/*" element={
            <>
              <main className="pb-20">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/market" element={<Market />} />
                  <Route path="/publish" element={<Publish user={user} />} />
                  <Route path="/collection" element={<Collection />} />
                  <Route path="/profile" element={<Profile user={user} />} />
                </Routes>
              </main>
              <TabBar />
            </>
          } />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
