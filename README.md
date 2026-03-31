# HTZ 合同台账管理系统

> 基于 Vue3 + FastAPI 的现代化合同与发票管理平台

## ✨ 功能特性

- 📋 **合同管理** — 增删改查、导入导出Excel
- 📄 **合同明细** — 类Excel编辑、批量导入导出
- 🧾 **发票管理** — 增删改查、关联合同
- 📊 **数据概览** — 统计图表、采购员分析
- 🎨 **现代UI** — 渐变色设计、深色侧边栏、响应式布局
- 🔐 **用户权限** — 管理员/普通用户

## 🚀 快速部署

### 一键部署（推荐）

```bash
bash -c "$(curl -fsSL https://gitee.com/alongchn/htz/raw/main/deploy.sh)"
```

或手动：

```bash
git clone https://gitee.com/alongchn/htz.git
cd htz
docker compose up -d
```

部署完成后访问：`http://你的IP:3000`

### 默认账号

- 用户名：`admin`
- 密码：`admin123`

## 📦 更新方法

```bash
cd htz
git pull
docker compose up -d --build
```

或直接运行：
```bash
bash deploy.sh
```

## 🛠 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 5671

# 前端（另开终端）
cd frontend
npm install
npm run dev
```

## 📁 项目结构

```
htz/
├── backend/              # 后端 API (FastAPI)
│   ├── main.py           # 接口定义
│   ├── database.py       # 数据库模型 (SQLite)
│   ├── auth.py           # JWT 认证
│   ├── requirements.txt  # Python 依赖
│   └── Dockerfile
├── frontend/             # 前端 (Vue3 + Element Plus)
│   ├── src/views/        # 页面组件
│   ├── nginx.conf        # Nginx 配置
│   └── Dockerfile
├── docker-compose.yml    # Docker 编排
├── deploy.sh             # 一键部署脚本
└── README.md
```

## 🔧 环境要求

- Docker >= 20.10
- Docker Compose v2
- 或：Python 3.10+ & Node.js 18+

## 📝 更新日志

### v1.1.0 (2026-04-01)
- ✅ 发票附件上传功能（支持 PDF、图片、Excel、Word）
- ✅ 附件存储到 `data/uploads/invoice_attachments/` 目录
- ✅ 发票列表显示附件状态（有附件显示📎查看，无附件显示上传按钮）
- ✅ 新增/编辑发票时可同时上传附件
- ✅ 合同号可点击跳转到合同详情
- ✅ 数据库新增附件字段

### v1.0.0 (2026-03-31)
- ✅ 合同管理（增删改查、导入导出）
- ✅ 合同明细管理（弹窗编辑、Excel导入导出）
- ✅ 发票管理（增删改查、关联合同）
- ✅ 数据概览（统计卡片、采购员分析、状态分布）
- ✅ 采购员颜色标签（文旭=蓝、沈薇=绿、熊佳新=橙、谭谭=红、陈民=灰、李赛=紫）
- ✅ 合同状态四级流程：进行中 → 待开票 → 待回款 → 已完结
- ✅ 订货/交货进度条
- ✅ 登录认证（JWT）
- ✅ Docker 部署支持
- ✅ 一键部署脚本
- ✅ 前端 Nginx 生产构建
- ✅ Gitee 仓库同步

## 📄 License

MIT
