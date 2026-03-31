#!/bin/bash
# HTZ 一键部署/更新脚本
# 在飞牛主机上使用

set -e

REPO_URL="https://github.com/CHNMRLiu/HTZ.git"
DIR_NAME="HTZ"

echo "🔄 HTZ 部署脚本"

if [ -d "$DIR_NAME" ]; then
    echo "📦 检测到已有目录，正在更新..."
    cd "$DIR_NAME"
    git pull origin main
else
    echo "📥 首次部署，正在克隆..."
    git clone "$REPO_URL"
    cd "$DIR_NAME"
fi

echo "🐳 启动 Docker..."
docker compose down 2>/dev/null || true
docker compose up -d --build

echo ""
echo "✅ 部署完成！"
echo "   前端: http://$(hostname -I | awk '{print $1}'):3000"
echo "   后端: http://$(hostname -I | awk '{print $1}'):5671"
echo "   账号: admin / admin123"
