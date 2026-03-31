#!/bin/bash
# HTZ 一键部署/更新脚本
# 适用于：飞牛NAS、Linux服务器、Docker环境
# 用法：bash deploy.sh

set -e

REPO_URL="https://gitee.com/alongchn/htz.git"
DIR_NAME="htz"

echo "=========================================="
echo "  HTZ 合同台账管理系统 - 部署脚本 v2.0"
echo "=========================================="
echo ""

# 检查依赖
check_deps() {
    if ! command -v git &> /dev/null; then
        echo "❌ 未安装 git"
        echo "   安装命令：apt install git / yum install git"
        echo "   飞牛NAS：在套件中心搜索 Git 安装"
        exit 1
    fi
    if ! command -v docker &> /dev/null; then
        echo "❌ 未安装 docker"
        echo "   飞牛NAS：在套件中心搜索 Docker 安装"
        exit 1
    fi
    if ! docker compose version &> /dev/null 2>&1; then
        echo "❌ docker compose 不可用"
        echo "   请确保 Docker 版本 >= 20.10"
        exit 1
    fi
    echo "✅ 依赖检查通过"
}

check_deps

# 克隆或更新
if [ -d "$DIR_NAME" ]; then
    echo ""
    echo "📦 检测到已有目录，检查更新..."
    cd "$DIR_NAME"
    git fetch origin main
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    if [ "$LOCAL" = "$REMOTE" ]; then
        echo "✅ 已是最新版本"
        echo ""
        read -p "是否强制重新构建？(y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🔄 重新构建中..."
            docker compose down 2>/dev/null || true
            docker compose up -d --build
        fi
    else
        echo "🔄 发现新版本，更新中..."
        git pull origin main
        echo "📦 重新构建并启动..."
        docker compose down 2>/dev/null || true
        docker compose up -d --build
        echo "✅ 更新完成！"
    fi
else
    echo ""
    echo "📥 首次部署，克隆仓库..."
    git clone "$REPO_URL" "$DIR_NAME"
    cd "$DIR_NAME"
    
    echo "📁 创建数据目录..."
    mkdir -p data
    
    echo "🐳 构建并启动 Docker 容器..."
    docker compose up -d --build
    echo "✅ 首次部署完成！"
fi

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "📊 服务状态："
docker compose ps

# 获取本机IP
IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")

echo ""
echo "=========================================="
echo "  ✅ HTZ 合同台账系统已启动"
echo "=========================================="
echo "  前端地址: http://${IP}:3000"
echo "  后端地址: http://${IP}:5671/docs"
echo "  默认账号: admin / admin123"
echo "=========================================="
echo ""
echo "  常用命令："
echo "    查看日志: docker compose logs -f"
echo "    停止服务: docker compose down"
echo "    重启服务: docker compose restart"
echo "    更新系统: bash deploy.sh"
echo "=========================================="
