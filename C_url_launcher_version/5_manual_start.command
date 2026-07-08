#!/bin/bash
# Switch Flow Mode - 非 Premium 試玩啟動

cd "$(dirname "$0")"

line="================================================"
echo "$line"
echo "  Switch Flow Mode - 非 Premium 試玩"
echo "$line"
echo ""

python3 manual_flow.py start

echo ""
read -p "按 Enter 結束..."
