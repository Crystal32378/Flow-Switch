#!/bin/bash
# Switch Flow Mode - 非 Premium 試玩設定

cd "$(dirname "$0")"

line="================================================"
echo "$line"
echo "  Switch Flow Mode - 非 Premium 試玩設定"
echo "$line"
echo ""
echo "  這個版本不需要 Spotify Premium，也不需要 Web API 授權。"
echo "  你只要貼四個 Spotify playlist 連結，之後用 5_manual_start.command 選模式。"
echo ""

python3 manual_flow.py setup

echo ""
read -p "按 Enter 結束..."
