#!/bin/bash
# Switch Flow Mode — 抓 Playlist 填入 Track Pool
# 雙擊此檔即可執行：列出你的 playlist → 互動式把 playlist 抓進對應模式

cd "$(dirname "$0")"

line="================================================"

echo "$line"
echo "  Switch Flow Mode — 抓 Playlist"
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

echo "  這個工具會幫你把 Spotify Playlist 的曲目抓進 config.json，"
echo "  對應到四種模式："
echo ""
echo "    focus      → 🧘 專注       （建議：ambient / 純音樂 / 古典）"
echo "    push       → 🚀 推進       （建議：高能 J-Pop / K-Pop）"
echo "    cinematic  → 🎬 影視餘韻   （建議：soundtrack / 史詩配樂）"
echo "    live       → 🎸 現場戒斷   （建議：Live 版本歌曲）"
echo ""
echo "  你需要先在 Spotify App 內建好對應的 playlist，每個至少 5 首。"
echo "  沒有現成的？現在就開 Spotify App 建一個，建完再回來。"
echo ""
echo "  按 Enter 開始列出你的 playlist..."
read -p ""

# ---------- 列出 playlist ----------
echo ""
echo "--- 你的所有 Playlist ---"
python build_pool.py list
echo ""

# ---------- 互動式迴圈 ----------
while true; do
    echo "$line"
    echo "  抓取 Playlist"
    echo "$line"
    echo ""
    echo "  四種模式目前狀態："
    python -c "
import json
cfg = json.load(open('config.json'))
for key, label in [('focus_tracks','🧘 專注'), ('push_tracks','🚀 推進'), ('cinematic_tracks','🎬 影視餘韻'), ('live_tracks','🎸 現場戒斷')]:
    items = cfg.get(key, [])
    valid = [x for x in items if x and 'REPLACE_WITH' not in x]
    mark = '✓' if len(valid) >= 5 else ('⚠️' if len(valid) > 0 else '❌')
    print(f'    {mark} {label:12s} ({key}): {len(valid)} 首')
"
    echo ""
    echo "  接下來："
    echo "    1. 從上面的 playlist 清單複製其中一個 URL"
    echo "    2. 貼到下方"
    echo "    3. 輸入要寫入哪個模式（focus / push / cinematic / live）"
    echo "    4. 重複 4 次把四個模式都填滿"
    echo ""
    echo "  （直接按 Enter 結束）"
    echo ""

    read -p "  Playlist URL: " URL
    if [ -z "$URL" ]; then
        echo ""
        echo "  結束抓取。"
        break
    fi

    read -p "  寫入哪個模式？(focus/push/cinematic/live): " MODE

    # 驗證 mode
    case "$MODE" in
        focus|push|cinematic|live)
            ;;
        *)
            echo "  ✗ 不認識的模式：$MODE"
            echo "  可用：focus / push / cinematic / live"
            echo ""
            continue
            ;;
    esac

    echo ""
    python build_pool.py pull "$URL" "$MODE"
    echo ""
    echo "  按 Enter 繼續抓下一個，或下次直接按 Enter 結束"
    read -p ""
done

# ---------- 結束 ----------
echo ""
echo "$line"
echo "  完成！目前狀態："
echo "$line"
python -c "
import json
cfg = json.load(open('config.json'))
ready = 0
for key, label in [('focus_tracks','🧘 專注'), ('push_tracks','🚀 推進'), ('cinematic_tracks','🎬 影視餘韻'), ('live_tracks','🎸 現場戒斷')]:
    items = cfg.get(key, [])
    valid = [x for x in items if x and 'REPLACE_WITH' not in x]
    mark = '✓ 可用' if len(valid) >= 5 else ('⚠️ 不足 5 首' if len(valid) > 0 else '❌ 空')
    print(f'  {mark}  {label}: {len(valid)} 首')
    if len(valid) >= 5:
        ready += 1
print()
print(f'  {ready}/4 個模式已就緒')
if ready == 4:
    print()
    print('  🎉 全部就緒！雙擊「3_start.command」啟動托盤小工具')
else:
    print()
    print('  還有模式未就緒。可以隨時雙擊此檔再抓 playlist 進來。')
"
echo ""
read -p "按 Enter 結束..."
