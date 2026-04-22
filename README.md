# 🚗 车模星球

汽车模型交易与收藏管理平台，参考泡泡玛特风格。

![React](https://img.shields.io/badge/React-18-blue) ![Vite](https://img.shields.io/badge/Vite-5-brightgreen) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 功能特点

- 🛒 **交易市场** - 浏览、筛选、搜索车模商品
- 💎 **收藏管理** - 管理藏品、查看收益走势
- 💬 **实时聊天** - 买卖双方实时议价
- 📊 **价格行情** - 各品牌价格趋势分析
- 📱 **跨平台** - Web + iOS + Android

## 技术栈

| 前端 | 后端 | 数据库 | 打包 |
|------|------|--------|------|
| React 18 | FastAPI | SQLite | Capacitor |
| Vite 5 | Uvicorn | SQLAlchemy | iOS/Android |
| TailwindCSS | Python 3.11 | aiosqlite | Vercel/Railway |

## 本地开发

### 前端

```bash
cd frontend
npm install
npm run dev      # 开发服务器 http://localhost:5173
npm run build    # 生产构建
```

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000  # API http://localhost:8000
```

## 一键部署

### 前端 → Vercel（免费）

1. 打开 https://vercel.com/new
2. Import `qilixuan/car-model-app`
3. Root Directory: `frontend`
4. Framework Preset: `Vite`
5. Build Command: `npm run build`
6. Output Directory: `dist`
7. 点击 Deploy！

### 后端 → Railway（免费额度）

1. 打开 https://railway.app/new
2. 选择 "Deploy from GitHub repo"
3. 选择 `qilixuan/car-model-app`
4. Root Directory: `backend`
5. Railway 自动检测 Python + FastAPI
6. 添加环境变量（可选）：
   - `DATABASE_URL=sqlite:///./car_model.db`
7. 点击 Deploy！

部署完成后，把后端的 URL（如 `https://xxx.railway.app`）填入前端的 `src/api/api.js` 中的 `BASE_URL`。

## 目录结构

```
car_model_app/
├── frontend/
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── components/     # 公共组件
│   │   ├── store/          # Zustand 状态管理
│   │   ├── api/            # API 调用层
│   │   └── data/           # 模拟数据
│   ├── ios/                # iOS 原生项目
│   └── android/            # Android 原生项目
├── backend/
│   ├── app/
│   │   ├── routers/        # API 路由
│   │   ├── models.py       # 数据模型
│   │   └── main.py         # FastAPI 入口
│   └── requirements.txt
└── README.md
```

## API 文档

后端部署后访问：`https://your-backend.railway.app/docs`

## License

MIT
