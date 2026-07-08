#!/bin/bash
# Switch Flow Mode — 第一次設定
# 雙擊此檔即可執行：檢查 Python → 建虛擬環境 → 裝套件 → 跑 Spotify 授權

cd "$(dirname "$0")"

# 顯示用分隔線
line="================================================"

echo "$line"
echo "  Switch Flow Mode — 第一次設定"
echo "$line"
echo ""

# ---------- [0/4] 檢查 Spotify App 設定 ----------
if [ ! -f ".env" ]; then
    echo "[0/4] 建立 Spotify App 設定檔..."
    echo ""
    cp .env.example .env
    echo "  已建立 .env。請用文字編輯器打開它，填入："
    echo "    SPOTIFY_CLIENT_ID"
    echo "    SPOTIFY_CLIENT_SECRET"
    echo ""
    echo "  填完並存檔後，回到這個視窗按 Enter 繼續。"
    open -a TextEdit .env 2>/dev/null || true
    read -p "按 Enter 繼續..."
fi

if grep -q "your_client_id_here\|your_client_secret_here" .env; then
    echo ""
    echo "  ✗ .env 還是範本內容，尚未填入 Spotify App 金鑰"
    echo "  請打開 .env 填入真實 SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET"
    echo ""
    read -p "按 Enter 結束..."
    exit 1
fi

# ---------- [1/4] 檢查 Python ----------
echo "[1/4] 檢查 Python..."
echo ""

if command -v python3 &> /dev/null; then
    PYVER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo "  ✓ 找到 Python $PYVER"

    # 檢查版本 ≥ 3.9
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3,9) else 1)'; then
        echo "  ✓ 版本符合（需要 3.9+）"
    else
        echo ""
        echo "  ✗ Python 版本太舊（$PYVER），需要 3.9 以上"
        echo ""
        echo "  請到以下網址下載安裝最新版 Python："
        echo "    https://www.python.org/downloads/"
        echo ""
        echo "  安裝完成後，關掉這個視窗，重新雙擊此檔案。"
        echo ""
        read -p "按 Enter 結束..."
        exit 1
    fi
else
    echo "  ✗ 找不到 Python"
    echo ""
    echo "  請到以下網址下載安裝 Python 3（選 macOS 64-bit universal2 installer）："
    echo "    https://www.python.org/downloads/"
    echo ""
    echo "  安裝完成後，關掉這個視窗，重新雙擊此檔案。"
    echo ""
    read -p "按 Enter 結束..."
    exit 1
fi

echo ""

# ---------- [2/4] 建立虛擬環境 + 裝套件 ----------
echo "[2/4] 建立虛擬環境並安裝套件..."
echo ""

if [ ! -d ".venv" ]; then
    echo "  → 建立虛擬環境..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "  ✗ 建立虛擬環境失敗"
        read -p "按 Enter 結束..."
        exit 1
    fi
else
    echo "  → 虛擬環境已存在，跳過"
fi

# 啟用虛擬環境
source .venv/bin/activate

echo "  → 升級 pip..."
pip install --upgrade pip --quiet

echo "  → 安裝 requirements.txt 內的套件（spotipy / pystray / Pillow / python-dotenv）..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo ""
    echo "  ✗ 套件安裝失敗，請看上方錯誤訊息"
    echo "  常見原因：網路問題。請確認網路連線正常後重試。"
    read -p "按 Enter 結束..."
    exit 1
fi

echo "  ✓ 套件安裝完成"
echo ""

# ---------- [3/4] 跑 Spotify 授權 ----------
echo "[3/4] 啟動 Spotify 授權流程..."
echo ""
echo "  接下來會發生這些事："
echo "    1. 終端機會印出一串網址"
echo "    2. 瀏覽器會自動開啟 Spotify 授權頁（若沒自動開，複製網址貼到瀏覽器）"
echo "    3. 在瀏覽器中按「Agree / 同意」"
echo "    4. 瀏覽器會跳到 http://127.0.0.1:8888/callback?... 然後顯示空白頁"
echo "       這是正常的，不用管它"
echo "    5. 回到這個終端機視窗，看到 ✓ 授權成功 就完成了"
echo ""
echo "  按 Enter 開始..."
read -p ""

python get_token.py
RESULT=$?

echo ""

if [ $RESULT -ne 0 ]; then
    echo "  ✗ 授權流程失敗，請看上方錯誤訊息"
    echo "  常見原因："
    echo "    - Redirect URI 在 Spotify Dashboard 設錯（應為 http://127.0.0.1:8888/callback）"
    echo "    - 你的 Spotify 帳號 email 沒加進 App 的 User Management 白名單"
    echo ""
    read -p "按 Enter 結束..."
    exit 1
fi

# ---------- [4/4] 完成 ----------
echo "$line"
echo "  [4/4] ✓ 設定完成！"
echo "$line"
echo ""
echo "  下一步："
echo "    1. 在 Spotify App 內隨便建 4 個小 playlist（每個 5 首以上即可）"
echo "       例如：「專注用」「健身用」「電影配樂」「Live 版」"
echo "    2. 雙擊「2_pull_playlists.command」把 playlist 抓進來"
echo "    3. 雙擊「3_start.command」啟動托盤小工具"
echo ""
read -p "按 Enter 結束..."
