# 战术视界 - 电竞对局复盘与心态指导智能体

## 项目简介

"战术视界"是一款专为大众电竞玩家设计的AI智能体，依托腾讯混元大模型技术，提供"技术复盘+情感疏导"双核心服务。以王者荣耀李白IP风格为交互载体，帮助玩家在对局失利后进行战术分析和心态调整。

## 核心功能

- **多模态对局复盘解析**：AI分析对局数据，用通俗易懂的李白风格语言输出复盘报告
- **王者荣耀IP式情绪疏导**：以李白潇洒侠客角色口吻进行共情式安抚和励志鼓励
- **个性化战术优化指导**：基于玩家习惯生成专属上分建议
- **全程心态管理**：记录心态变化轨迹，提供赛前预热指导

## 技术架构

### 前端
- Vue 3 + Vite + TypeScript
- Element Plus UI 组件库
- Pinia 状态管理
- Tailwind CSS 样式框架
- Axios HTTP 客户端

### 后端
- Python FastAPI
- SQLAlchemy ORM
- SQLite 数据库
- 腾讯混元大模型 SDK

## 项目结构

```
├── frontend/                          # Vue 3 前端项目
│   ├── src/
│   │   ├── router/                    # 路由配置
│   │   ├── stores/                    # Pinia 状态管理
│   │   ├── api/                       # API 请求封装
│   │   ├── components/                # 通用组件
│   │   ├── views/                     # 页面组件
│   │   ├── types/                     # TypeScript 类型定义
│   │   └── styles/                    # 全局样式
│
├── backend/                           # FastAPI 后端项目
│   ├── app/
│   │   ├── routers/                   # API 路由
│   │   ├── services/                  # 业务逻辑服务
│   │   ├── models.py                  # 数据模型
│   │   ├── schemas.py                 # Pydantic 模型
│   │   ├── database.py                # 数据库配置
│   │   └── config.py                  # 应用配置
│   ├── run.py                         # 应用启动脚本
│   ├── init_db.py                     # 数据库初始化脚本
│   └── requirements.txt               # Python 依赖
└── README.md                          # 项目说明
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- npm 或 yarn

### 后端启动

1. 进入后端目录：
```bash
cd backend
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填写腾讯云 API 凭证：
```env
TENCENT_SECRET_ID=your_secret_id_here
TENCENT_SECRET_KEY=your_secret_key_here
```

4. 初始化数据库：
```bash
python init_db.py
```

5. 启动服务：
```bash
python run.py
```

后端服务将在 `http://localhost:8000` 运行。

### 前端启动

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 配置 API 地址（可选）：

编辑 `.env` 文件（如不存在则创建）：
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

4. 启动开发服务器：
```bash
npm run dev
```

前端应用将在 `http://localhost:5173` 运行。

## 使用说明

### 1. 对局复盘

- 选择游戏类型和对局结果
- 填写 KDA 数据（可选）
- 详细描述对局情况
- 点击"开始复盘分析"
- 查看 AI 生成的复盘报告

### 2. 情绪疏导

- 选择情绪场景或手动输入
- 与李白角色进行对话
- 查看情绪状态指示器
- 接收个性化的情绪疏导

### 3. 心态管理

- 查看心态日历，了解情绪变化
- 获取赛前心态预热指导
- 查看成长笔记和统计数据

## API 接口

### 情绪疏导

- `POST /api/emotion/analyze` - 情绪分析（流式）
- `GET /api/emotion/history` - 获取情绪历史
- `GET /api/emotion/stats` - 获取情绪统计

### 对局复盘

- `POST /api/review/analyze` - 对局分析（流式）
- `GET /api/review/history` - 获取复盘历史
- `GET /api/review/stats` - 获取复盘统计

### 心态管理

- `GET /api/mindset/records` - 获取心态记录
- `GET /api/mindset/calendar/{year}/{month}` - 获取心态日历
- `GET /api/mindset/trend` - 获取心态趋势
- `GET /api/mindset/pregame-guidance` - 获取赛前指导

## 设计风格

采用"王者荣耀-水墨国风"设计风格，以李白角色的视觉特质为核心设计语言：

- **主色调**：墨蓝/暗金 (#1A1A2E, #C9A227)
- **辅助色**：水墨渐变纹理
- **字体**：Noto Sans SC
- **布局**：左侧固定导航 + 右侧主内容区

## 开发说明

### 添加新功能

1. 后端：在 `app/services/` 中添加服务逻辑
2. 后端：在 `app/routers/` 中添加 API 路由
3. 前端：在 `src/api/` 中添加 API 调用方法
4. 前端：在 `src/views/` 中创建页面组件
5. 前端：在 `src/router/index.ts` 中添加路由

### 数据库迁移

如需修改数据模型：

1. 修改 `app/models.py`
2. 删除旧数据库文件 `tactical_vision.db`
3. 重新运行 `python init_db.py`

## 注意事项

- 使用前必须配置腾讯云 API 凭证
- 首次启动需要初始化数据库
- 开发环境使用 SQLite，生产环境建议切换到 MySQL/PostgreSQL
- 混元大模型调用会产生费用，请注意 API 调用次数

## 许可证

MIT License

## 联系

如有问题或建议，欢迎提交 Issue。
