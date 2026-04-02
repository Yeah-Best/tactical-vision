# 战术视界 - 电竞对局复盘与心态指导智能体

## 项目简介

"战术视界"是一款专为大众电竞玩家设计的 AI 智能体，依托腾讯混元大模型技术，提供"技术复盘+情感疏导"双核心服务。以王者荣耀李白 IP 风格为交互载体，帮助玩家在对局失利后进行战术分析和心态调整。

## 核心功能

- **多模态对局复盘解析**：AI 分析对局数据，用通俗易懂的李白风格语言输出复盘报告
- **王者荣耀 IP 式情绪疏导**：以李白潇洒侠客角色口吻进行共情式安抚和励志鼓励
- **个性化战术优化指导**：基于玩家习惯生成专属上分建议
- **全程心态管理**：记录心态变化轨迹，提供赛前预热指导
- **游戏版本实时获取**：支持王者荣耀、英雄联盟、无畏契约等多款热门游戏的版本信息
- **智能语音播报**：使用浏览器内置 Web Speech API 实现情绪化语音朗读

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

或者使用便捷启动脚本：

```bash
# Windows 双击运行
restart-backend.bat
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

4. 启动开发服务器（推荐方式）：

```bash
# Windows 双击运行
start-frontend.bat

# 或者使用 PowerShell
.\start-frontend.ps1
```

**重要提示：**
- 推荐使用 `http://127.0.0.1:5173` 访问（兼容性最好）
- 如果使用 `http://localhost:5173` 无法访问，请使用 `http://127.0.0.1:5173`
- 网络其他设备访问：`http://192.168.192.1:5173`（根据实际 IP 调整）

传统启动方式（可能不兼容 localhost）：

```bash
npm run dev
```

前端应用将在 `http://127.0.0.1:5173` 或 `http://localhost:5173` 运行。

## 使用说明

### 1. 对局复盘

- 选择游戏类型和对局结果
- 填写 KDA 数据（可选）
- 详细描述对局情况
- 可点击"获取最新版本"自动填充游戏版本号
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

### 游戏版本

- `GET /api/game-version/latest?game=<游戏名称>` - 获取指定游戏的最新版本
- `GET /api/game-version/all` - 获取所有支持游戏的版本信息
- `GET /api/game-version/supported-games` - 获取支持的游戏列表

**支持的游戏：**
- `honor_of_kings` / `王者荣耀` - 王者荣耀
- `lol` / `英雄联盟` - 英雄联盟
- `valorant` / `无畏契约` - 无畏契约

**说明：**
- 版本信息支持网络实时抓取和本地缓存
- 当网络请求失败时，会返回缓存版本或默认版本信息
- 版本信息包含版本号、更新时间和更新内容摘要

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
2. 删除旧数据库文件 `backend/tactical_vision.db`
3. 重新运行 `python init_db.py`

### 项目清理

删除临时文件和缓存：

```bash
# Windows
rd /s /q backend\__pycache__
rd /s /q backend\app\__pycache__
rd /s /q backend\app\routers\__pycache__
rd /s /q backend\app\services\__pycache__
```

或者在 `.gitignore` 中添加：

```
__pycache__/
*.pyc
*.db
*.log
```

## 注意事项

- 使用前必须配置腾讯云 API 凭证
- 首次启动需要初始化数据库
- 开发环境使用 SQLite，生产环境建议切换到 MySQL/PostgreSQL
- 混元大模型调用会产生费用，请注意 API 调用次数
- 语音功能使用浏览器内置的 Web Speech API，无需额外依赖或后端支持
- 游戏版本抓取功能依赖于网络环境，如果抓取失败会使用本地缓存或默认数据

## 语音功能说明

本项目使用浏览器内置的 Web Speech API 实现语音朗读功能，支持：

- **自动检测并使用中文语音**
- **音量调节**：0% - 100%
- **语速调节**：0.5x - 2.0x
- **根据情绪自动调整语调和语速**：
  - 烦躁：较慢语速 + 较低音调
  - 紧张：较快语速 + 较高音调
  - 喜悦：轻快语速 + 高音调
  - 平静：正常语速 + 正常音调

- **自动检测并使用中文语音**
- **音量调节**：0% - 100%
- **语速调节**：0.5x - 2.0x
- **根据情绪自动调整语调和语速**：
  - 烦躁：较慢语速 + 较低音调
  - 紧张：较快语速 + 较高音调
  - 喜悦：轻快语速 + 高音调
  - 平静：正常语速 + 正常音调

### 兼容性

Web Speech API 支持以下浏览器：
- Chrome 33+
- Edge 14+
- Safari 7+
- Firefox 62+ (部分支持)

### 浏览器语音设置

如果语音列表中没有中文语音或语音质量不佳，请在浏览器设置中添加中文语音包：

**Windows**：
1. 设置 > 时间和语言 > 语言
2. 添加"中文（简体）"
3. 下载语音包

**Mac**：
1. 系统设置 > 通用 > 语言与地区
2. 添加中文并下载语音

**Linux**：
1. 安装 `espeak` 或 `festival` 语音合成引擎
2. 根据发行版使用包管理器安装

## 故障排除

### 语音功能无法使用

如果语音测试失败或无法播放语音，请尝试以下步骤：

1. **检查浏览器兼容性**：确保使用支持 Web Speech API 的浏览器（推荐 Chrome 或 Edge）

2. **检查浏览器语音设置**：
   - 确保已安装中文语音包
   - 在浏览器设置中查看可用语音列表

3. **浏览器权限**：
   - 确保浏览器允许使用语音功能
   - 检查是否有隐私设置阻止语音合成

4. **测试浏览器支持**：
   在浏览器控制台执行：
   ```javascript
   console.log('Speech Synthesis supported:', 'speechSynthesis' in window)
   console.log('Available voices:', window.speechSynthesis?.getVoices())
   ```

5. **刷新页面**：有时需要刷新页面才能正确加载语音列表

### 常见错误

- **没有可用语音**：需要在操作系统设置中安装中文语音包
- **语音质量不佳**：浏览器使用的语音质量取决于操作系统安装的语音包
- **语音列表为空**：某些浏览器需要页面加载完成后才能获取语音列表，请稍等片刻或刷新页面

## 游戏版本功能说明

本项目支持自动获取多款热门游戏的最新版本信息：

### 支持的游戏

- **王者荣耀**（honor_of_kings）
- **英雄联盟**（lol）
- **无畏契约**（valorant）

### 版本获取方式

1. **网络抓取**：尝试从游戏官网实时抓取最新版本信息
2. **本地缓存**：如果网络请求失败，使用上次成功获取的缓存数据
3. **默认版本**：首次使用或无缓存时，返回预设的默认版本信息

### 使用方法

在复盘页面：
1. 选择游戏类型
2. 点击"获取最新版本"按钮
3. 系统自动获取并填充最新版本号
4. 继续填写对局信息

### 版本信息包含

- **游戏名称**：支持的游戏名称
- **版本号**：当前最新版本
- **更新时间**：版本发布日期
- **更新内容**：版本更新摘要（部分游戏支持）
- **来源链接**：官方版本更新页面链接

### 注意事项

- 版本抓取功能依赖于网络环境和目标网站的可用性
- 如果官网页面结构发生变化，可能导致抓取失败
- 在网络受限环境下，系统会自动使用缓存或默认数据
- 版本信息仅供参考，请以官方发布的版本为准

## 许可证

MIT License

## 联系

如有问题或建议，欢迎提交 Issue。
