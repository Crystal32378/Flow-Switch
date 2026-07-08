#!/bin/bash
# Switch Flow Mode — 啟動托盤小工具
# 雙擊此檔即可啟動系統托盤的 Spotify 換檔器

cd "$(dirname "$0")"

line="================================================"

echo "$line"
echo "  Switch Flow Mode — 啟動"
echo "$line"
echo ""

# 檢查前置條件
if [ ! -d ".venv" ]; then
    echo "  ✗ 尚未完成第一次設定"
    echo "  請先雙擊「1_setup.command」"
    echo ""
    read -p "按 Enter 結束..."
    exit 1
fi

if [ ! -f ".spotify_cache.json" ]; then
    echo "  ✗ 尚未完成 Spotify 授權"
    echo "  請先雙擊「1_setup.command」"
    echo ""
    read -p "按 Enter 結束..."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "  ✗ 找不到 .env"
    echo "  請先複製 .env.example 為 .env，或重跑「1_setup.command」"
    echo ""
    read -p "按 Enter 結束..."
    exit 1
fi

# 啟用虛擬環境
source .venv/bin/activate

echo "  啟動中...這個視窗請保持開啟，關掉視窗 = 程式結束"
echo "  系統托盤（螢幕右上角）會出現黑色圓形圖標"
echo ""
echo "  使用方式："
echo "    1. 先在任一裝置（Mac Spotify App / 手機 / Web Player）打開 Spotify"
echo "    2. 點托盤的黑色圓形圖標 → 選模式"
echo "    3. Spotify 自動開始播放該模式的 30 首歌"
echo ""
echo "  結束程式：從托盤選單按「❌ 結束」"
echo ""
echo "$line"
echo ""

python flow_switcher.py

# 如果程式結束了（不正常或被關掉），顯示錯誤訊息給使用者看
EXIT_CODE=$?
echo ""
echo "$line"
if [ $EXIT_CODE -ne 0 ]; then
    echo "  ⚠️ 程式結束（exit code: $EXIT_CODE）"
    echo "  若是錯誤，請看上方訊息。常見原因："
    echo "    - Spotify 沒開 → 先開 Spotify App 再啟動此檔"
    echo "    - 授權過期 → 重跑「1_setup.command」"
    echo "    - pool 未填 → 跑「2_pull_playlists.command」"
else
    echo "  程式已正常結束"
fi
echo "$line"
echo ""
read -p "按 Enter 關閉視窗..."
