#!/bin/bash
# HTZ 一键部署/更新脚本
# 适用于：飞牛NAS、Linux服务器、WSL
# 用法：bash deploy.sh

set -e

REPO_URL="https://github.com/CHNMRLiu/HTZ.git"
DIR_NAME="HTZ"

echo "==========================================="
echo "  HTZ 合同台账管理系统 - 部署脚本"
echo "==========================================="
echo ""

# 检查依赖
check_deps() {
    if ! command -v git &> /dev/null; then
        echo "❌ 未安装 git，请先安装: apt install git / yum install git"
        exit 1
    fi
    if ! command -v docker &> /dev/null; then
        echo "❌ 未安装 docker，请先安装 Docker"
        exit 1
    fi
}

check_deps

# 克隆或更新
if [ -d "$DIR_NAME" ]; then
    echo "📦 检测到已有目录，正在拉取最新代码..."
    cd "$DIR_NAME"
    git fetch origin main
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    if [ "$LOCAL" = "$REMOTE" ]; then
        echo "✅ 已是最新版本，无需更新"
    else
        echo "🔄 发现新版本，正在更新..."
        git pull origin main
        echo "📦 重新构建并启动..."
        docker compose down 2>/dev/null || true
        docker compose up -d --build
        echo "✅ 更新完成！"
    fi
else
    echo "📥 首次部署，正在克隆仓库..."
    git clone "$REPO_URL"
    cd "$DIR_NAME"
    echo "🐳 构建并启动 Docker 容器..."
    docker compose up -d --build
    echo "✅ 首次部署完成！"
fi

# 获取本机IP
IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")

echo ""
echo "==========================================="
echo "  ✅ HTZ 合同台账系统已启动"
echo "==========================================="
echo "  前端地址: http://${IP}:3000"
echo "  后端地址: http://${IP}:5671/docs"
echo "  默认账号: admin / admin123"
echo "==========================================="
echo ""
echo "  更新命令: cd HTZ && bash deploy.sh"
echo "==========================================="
