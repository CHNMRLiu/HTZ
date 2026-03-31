#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 启动 HTZ 合同台账系统..."

# 启动后端
echo "📦 启动后端 (端口 5671)..."
cd backend
pip install -q -r requirements.txt 2>/dev/null
uvicorn main:app --host 0.0.0.0 --port 5671 &
BACKEND_PID=$!
cd ..

# 等后端启动
sleep 3

# 启动前端
echo "🎨 启动前端 (端口 5670)..."
cd frontend
npm run dev -- --host 0.0.0.0 --port 5670 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ HTZ 已启动！"
echo "   前端: http://localhost:5670"
echo "   后端: http://localhost:5671"
echo "   默认账号: admin / admin123"
echo ""
echo "按 Ctrl+C 停止所有服务"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
