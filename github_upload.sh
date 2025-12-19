#!/bin/bash

# Lit-Miner GitHub 快速上传脚本
# 使用方法：./github_upload.sh https://github.com/你的用户名/Lit-Miner.git

set -e  # 遇到错误立即退出

echo "📚 Lit-Miner GitHub 上传脚本"
echo "================================"
echo ""

# 检查是否提供了仓库地址
if [ -z "$1" ]; then
    echo "❌ 错误：请提供GitHub仓库地址"
    echo ""
    echo "用法："
    echo "  ./github_upload.sh https://github.com/你的用户名/Lit-Miner.git"
    echo ""
    echo "📝 请先在GitHub创建仓库，然后复制仓库地址"
    exit 1
fi

REPO_URL="$1"

echo "🔍 检查项目状态..."
echo ""

# 检查是否已经是Git仓库
if [ -d ".git" ]; then
    echo "✅ 已存在Git仓库"
else
    echo "📝 初始化Git仓库..."
    git init
    echo "✅ Git仓库初始化完成"
fi

echo ""
echo "📦 添加文件到Git..."
git add .

echo ""
echo "📊 以下文件将被提交："
git status --short

echo ""
echo "💾 创建提交..."
git commit -m "Initial commit: Lit-Miner v1.0 - AI-Powered Literature Mining & Review Generation" || echo "ℹ️  没有新的更改需要提交"

echo ""
echo "🌿 设置主分支..."
git branch -M main

echo ""
echo "🔗 关联远程仓库..."
git remote remove origin 2>/dev/null || true  # 移除旧的origin（如果有）
git remote add origin "$REPO_URL"

echo ""
echo "🚀 推送到GitHub..."
echo "⚠️  如果提示输入密码，请使用Personal Access Token而非账号密码"
echo ""

git push -u origin main

echo ""
echo "================================"
echo "✅ 上传成功！"
echo ""
echo "🎉 你的项目已经上传到："
echo "   $REPO_URL"
echo ""
echo "📖 查看在线仓库："
echo "   ${REPO_URL%.git}"
echo ""
