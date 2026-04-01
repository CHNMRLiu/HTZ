# HTZ 合同台账管理系统 v2.0

> 基于 Vue3 + FastAPI 的现代化合同与发票管理平台

## ✨ 功能特性

- 📋 **合同管理** — 增删改查、批量操作、多条件搜索、排序、导入导出 Excel
- 📄 **合同明细** — 类 Excel 编辑、批量导入导出、汇总统计
- 🧾 **发票管理** — 增删改查、关联合同、附件上传
- 📊 **数据概览** — 统计卡片、月度趋势图、状态分布、采购员排行、到期提醒
- 🔔 **到期提醒** — 已过期红色高亮、30天内到期黄色提醒
- 🎨 **现代 UI** — 深色侧边栏、渐变设计、响应式布局、流畅动画
- 🔐 **用户权限** — 管理员/普通用户、用户管理
- 📦 **批量操作** — 批量删除、批量更新状态
- 🔍 **高级搜索** — 关键字、状态、采购员、类型、部门、日期范围

## 🚀 快速部署

### Docker 一键部署（推荐）

```bash
git clone https://gitee.com/alongchn/htz.git
cd htz
docker compose up -d
```

访问：`http://<你的IP>:3000`

### 默认账号

- 用户名：`admin`
- 密码：`admin123`

## 📦 更新方法

```bash
cd htz
git pull
docker compose up -d --build
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
│   ├── main.py           # API 接口（v2.0 重构）
│   ├── database.py       # 数据库模型 (SQLite + SQLAlchemy)
│   ├── auth.py           # JWT 认证
│   ├── requirements.txt  # Python 依赖
│   └── Dockerfile
├── frontend/             # 前端 (Vue3 + Element Plus)
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── api.js        # Axios 封装
│   │   ├── router.js     # 路由配置
│   │   ├── main.js       # 入口
│   │   └── App.vue       # 根组件
│   ├── nginx.conf        # Nginx 配置
│   └── Dockerfile
├── docker-compose.yml    # Docker 编排
├── deploy.sh             # 一键部署脚本
├── CHANGELOG.md          # 更新日志
└── README.md
```

## 📝 更新日志

详见 [CHANGELOG.md](./CHANGELOG.md)

### v2.0.0 亮点
- ✅ 全面重构前后端代码
- ✅ 批量操作（删除、更新状态）
- ✅ 高级搜索与排序
- ✅ 月度趋势统计图
- ✅ 到期合同提醒
- ✅ 更好的表单验证
- ✅ 更流畅的 UI 动画

## 📄 License

MIT
