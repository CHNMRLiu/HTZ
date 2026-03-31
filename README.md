# HTZ 合同台账系统

## 功能
- 合同管理（增删改查、导入导出Excel）
- 发票管理（增删改查、导出Excel）
- 数据概览统计
- 用户权限（管理员/普通用户）

## 快速启动

### 本地开发
```bash
bash start.sh
```

### Docker部署
```bash
docker compose up -d
```

## 访问
- 前端: http://localhost:5670
- 后端API: http://localhost:5671/docs
- 默认账号: admin / admin123

## 导入数据
Excel格式（第一行为表头）：
| 序号 | 供应合同号 | 签订日期 | 合同金额 | 合同状态 | 采购员 | 合同内容 | 开票信息 |
