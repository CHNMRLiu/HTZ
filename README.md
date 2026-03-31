# HTZ 合同台账管理系统

## 功能特性

- 📋 合同管理（增删改查、导入导出Excel）
- 📄 合同明细（类Excel编辑、批量导入导出）
- 🧾 发票管理（增删改查、导出Excel）
- 📊 数据概览（统计图表、采购员分析）
- 🔐 用户权限（管理员/普通用户）
- 🎨 现代化UI设计

## 技术栈

- **前端：** Vue3 + Element Plus + Vite
- **后端：** Python FastAPI + SQLite
- **部署：** Docker Compose

## 快速部署（飞牛NAS / Linux）

### 方法一：一键脚本（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/CHNMRLiu/HTZ/main/deploy.sh | bash
```

### 方法二：手动部署

```bash
# 1. 克隆项目
git clone https://github.com/CHNMRLiu/HTZ.git
cd HTZ

# 2. 启动服务
docker compose up -d

# 3. 访问
# 前端: http://你的IP:3000
# 后端: http://你的IP:5671/docs
```

### 方法三：本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 5671

# 前端（另开终端）
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```

## 默认账号

- 用户名：`admin`
- 密码：`admin123`

## 更新方法

```bash
cd HTZ
git pull origin main
docker compose up -d --build
```

## 项目结构

```
HTZ/
├── backend/              # 后端API
│   ├── main.py           # 接口定义
│   ├── database.py       # 数据库模型
│   ├── auth.py           # 认证模块
│   ├── requirements.txt  # Python依赖
│   └── Dockerfile
├── frontend/             # 前端页面
│   └── src/views/        # 页面组件
├── docker-compose.yml    # Docker编排
├── deploy.sh             # 一键部署脚本
└── README.md
```

## 环境要求

- Docker & Docker Compose
- 或者：Python 3.10+ & Node.js 18+

## License

Private - 仅限内部使用
