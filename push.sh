#!/bin/bash
# 获取当前时间作为默认 commit message
now=$(date "+%Y-%m-%d %H:%M:%S")
# 如果用户传了参数，就用参数作为 commit message，否则使用默认时间
msg=${1:-"auto commit: $now"}
echo "🔄 正在添加所有更改..."
git add .
echo "✅ 提交更改: $msg"
git commit -m "$msg"
echo "📤 推送到远程仓库..."
git push origin $(git rev-parse --abbrev-ref HEAD)
echo "🚀 推送完成！"