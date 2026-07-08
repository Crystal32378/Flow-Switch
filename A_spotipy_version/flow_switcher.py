"""
Switch Flow Mode — Spotify 情緒換檔器
極簡系統托盤小工具，一鍵切換四種音樂情境。

⚠️ 架構變更說明（2024/11 Spotify Web API 政策）：
  原 brief 設計使用 spotipy.recommendations() 自動生成，但 Spotify 自
  2024/11/27 起對新註冊 app 關閉 Recommendations / Audio Features API，
  本工具改用「本地 track pool + 隨機抽取」實作。
  精神不變：繞過混亂歌單，每次以 start_playback 啟動一組新的播放序列。
  詳見 README「為什麼不能用 recommendations」一節。

MVP 門檻：
  每個 pool 只要 ≥ 5 首即可啟動，先讓功能跑起來，歌池之後再慢慢擴。
  Pool ≥ 30 時隨機抽 30 首不重複；Pool 介於 5–29 時先全取再隨機補足到 30。

四種模式（每個對應 config.json 內一個 track pool）：
  🧘 專注       -> focus_tracks       （建議：ambient / classical / sleep）
  🚀 推進       -> push_tracks        （建議：高能 J-Pop / K-Pop）
  🎬 影視餘韻   -> cinematic_tracks   （建議：soundtrack / 史詩感）
  🎸 現場戒斷   -> live_tracks        （建議：Live 版本歌曲）

用法：
  1. python get_token.py        # 一次性授權
  2. python build_pool.py list  # 看自己的 playlist
  3. python build_pool.py pull "<playlist_url>" <mode>  # 抓曲目填 pool
     (重複 4 次把四個 pool 填滿)
  4. python flow_switcher.py    # 啟動托盤
"""

import json
import random
import sys
import threading
import time
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image, ImageDraw
import pystray

from spotify_auth import CACHE_PATH, REDIRECT_URI, SCOPES, load_spotify_settings

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"

# 每次播放序列的目標長度
PLAYLIST_SIZE = 30
# Pool 啟動門檻：低於此數量會拒絕執行（避免只有 1–2 首的尴尬體驗）
MIN_POOL_SIZE = 5


# ========== Spotify 客戶端 ==========

_spotify_lock = threading.Lock()
_spotify_client = None


def get_spotify_client() -> spotipy.Spotify:
    global _spotify_client
    with _spotify_lock:
        if _spotify_client is not None:
            return _spotify_client

        if not CACHE_PATH.exists():
            raise RuntimeError(
                "找不到 .spotify_cache.json。請先執行: python get_token.py"
            )

        client_id, client_secret = load_spotify_settings()
        auth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=REDIRECT_URI,
            scope=SCOPES,
            cache_path=str(CACHE_PATH),
        )
        _spotify_client = spotipy.Spotify(auth_manager=auth)
        return _spotify_client


# ========== 設定檔 ==========

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise RuntimeError("找不到 config.json，請先建立（參考 README 範例）。")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    # 過濾掉說明欄位
    cfg.pop("_說明", None)
    cfg.pop("_使用建議", None)
    return cfg


def filter_valid_uris(uris_or_ids: list[str]) -> list[str]:
    """把輸入統一成 spotify:track:xxx 形式，並過濾掉佔位符。"""
    result = []
    for u in uris_or_ids or []:
        if not u or "REPLACE_WITH" in u:
            continue
        if u.startswith("spotify:track:"):
            result.append(u)
        elif u.startswith("https://open.spotify.com/track/"):
            tid = u.split("/track/")[-1].split("?")[0]
            result.append(f"spotify:track:{tid}")
        else:
            # 假設是純 ID
            result.append(f"spotify:track:{u}")
    return result


# ========== Pool 抽樣 + 播放 ==========

def pick_random_pool(pool: list[str], n: int = PLAYLIST_SIZE) -> list[str]:
    """
    從 pool 組出一條長度 n 的播放序列。
      - pool 為空或 < MIN_POOL_SIZE：丟錯誤
      - pool ≥ n：隨機抽 n 首不重複
      - MIN_POOL_SIZE ≤ pool < n：先全取，再用隨機抽樣（可重複）補到 n，最後洗牌
    """
    if not pool:
        raise RuntimeError(
            "pool 是空的，請先用 build_pool.py 抓曲目，或手動編輯 config.json。"
        )
    if len(pool) < MIN_POOL_SIZE:
        raise RuntimeError(
            f"pool 只有 {len(pool)} 首，至少要 {MIN_POOL_SIZE} 才能啟動。"
            f"請先用 build_pool.py 多抓幾首進來。"
        )
    if len(pool) >= n:
        return random.sample(pool, n)
    # 不足 n：全取 + 隨機抽樣（可重複）補到 n
    result = list(pool)
    result.extend(random.choices(pool, k=n - len(pool)))
    random.shuffle(result)
    return result


def start_playback_sequence(sp: spotipy.Spotify, uris: list[str]) -> None:
    """
    以 start_playback 啟動一組新的播放序列。

    Spotify Web API 沒有「替換 queue」這件事，能做的最接近動作是：
    呼叫 start_playback(uris=[...])，把這批歌當成新的播放 context ——
    第一首立即播放，剩下的依序排在後面。原本的 queue 不會被清空，
    但因為新的 context 會從第一首開始播放，使用者體感就是「換歌了」。

    單次 uris 上限 100，本工具固定送 30 首。
    """
    devices = sp.devices()
    if not devices.get("devices"):
        raise RuntimeError(
            "找不到可用的 Spotify 裝置。請先在任一裝置（桌面/手機/Web）開啟 Spotify 並登入同一帳號。"
        )

    device_id = None
    for d in devices["devices"]:
        if d.get("is_active"):
            device_id = d["id"]
            break
    if device_id is None:
        device_id = devices["devices"][0]["id"]

    sp.start_playback(device_id=device_id, uris=uris)


# ========== 四種模式 ==========

def mode_focus(sp: spotipy.Spotify) -> list[str]:
    """🧘 專注：從 focus_tracks pool 抽樣組 30 首播放序列"""
    cfg = load_config()
    pool = filter_valid_uris(cfg.get("focus_tracks", []))
    uris = pick_random_pool(pool)
    start_playback_sequence(sp, uris)
    return uris


def mode_push(sp: spotipy.Spotify) -> list[str]:
    """🚀 推進：從 push_tracks pool 抽樣組 30 首播放序列"""
    cfg = load_config()
    pool = filter_valid_uris(cfg.get("push_tracks", []))
    uris = pick_random_pool(pool)
    start_playback_sequence(sp, uris)
    return uris


def mode_cinematic(sp: spotipy.Spotify) -> list[str]:
    """🎬 影視餘韻：從 cinematic_tracks pool 抽樣組 30 首播放序列"""
    cfg = load_config()
    pool = filter_valid_uris(cfg.get("cinematic_tracks", []))
    uris = pick_random_pool(pool)
    start_playback_sequence(sp, uris)
    return uris


def mode_live(sp: spotipy.Spotify) -> list[str]:
    """🎸 現場戒斷：從 live_tracks pool 抽樣組 30 首播放序列"""
    cfg = load_config()
    pool = filter_valid_uris(cfg.get("live_tracks", []))
    uris = pick_random_pool(pool)
    start_playback_sequence(sp, uris)
    return uris


# ========== Tray UI ==========

MODES = [
    ("🧘 專注", mode_focus),
    ("🚀 推進", mode_push),
    ("🎬 影視餘韻", mode_cinematic),
    ("🎸 現場戒斷", mode_live),
]


def _draw_circle(color: tuple[int, int, int, int]) -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((8, 8, 56, 56), fill=color)
    return img


_ICON_BLACK = _draw_circle((0, 0, 0, 255))      # 預設
_ICON_GRAY = _draw_circle((140, 140, 140, 255))  # 生成中
_ICON_RED = _draw_circle((200, 60, 60, 255))    # 錯誤


def trigger_mode(icon: pystray.Icon, mode_fn, label: str) -> None:
    """在獨立 thread 內跑模式，避免凍結選單。"""
    def worker():
        try:
            icon.icon = _ICON_GRAY
            icon.title = f"Switch Flow - 抽歌中 [{label}]"
            sp = get_spotify_client()
            uris = mode_fn(sp)
            icon.icon = _ICON_BLACK
            icon.title = f"Switch Flow ✓ {label}（已啟動 {len(uris)} 首播放序列）"
        except Exception as e:
            icon.icon = _ICON_RED
            icon.title = f"Switch Flow ❌ {label}: {e}"
            print(f"[Error] {label}: {e}", file=sys.stderr)
            time.sleep(2.0)
            icon.icon = _ICON_BLACK
            icon.title = "Switch Flow Mode"

    threading.Thread(target=worker, daemon=True).start()


def on_quit(icon: pystray.Icon, item) -> None:
    icon.stop()


def build_menu() -> pystray.Menu:
    items = []
    for label, fn in MODES:
        items.append(
            pystray.MenuItem(
                label,
                lambda icon, item, f=fn, l=label: trigger_mode(icon, f, l),
            )
        )
    items.append(pystray.Menu.SEPARATOR)
    items.append(pystray.MenuItem("❌ 結束", on_quit))
    return pystray.Menu(*items)


def main() -> None:
    try:
        load_spotify_settings()
    except RuntimeError as e:
        print("=" * 56)
        print(f"  {e}")
        print("  建立 Spotify App: https://developer.spotify.com/dashboard")
        print("=" * 56)
        sys.exit(1)

    if not CACHE_PATH.exists():
        print("=" * 56)
        print("  找不到 .spotify_cache.json")
        print("  請先執行: python get_token.py")
        print("=" * 56)
        sys.exit(1)

    # 啟動前檢查 pool 狀態
    try:
        cfg = load_config()
        print("目前各模式 pool 大小：")
        for label, fn in MODES:
            # 從 MODES 推回 config key
            key_map = {
                "🧘 專注": "focus_tracks",
                "🚀 推進": "push_tracks",
                "🎬 影視餘韻": "cinematic_tracks",
                "🎸 現場戒斷": "live_tracks",
            }
            key = key_map[label]
            count = len(filter_valid_uris(cfg.get(key, [])))
            if count == 0:
                marker = "❌ "
            elif count < MIN_POOL_SIZE:
                marker = "⚠️  "
            else:
                marker = "   "
            print(f"  {marker}{label}: {count} 首")
        print()
    except Exception as e:
        print(f"[警告] 讀 config.json 失敗: {e}\n")

    icon = pystray.Icon(
        "switch_flow_mode",
        _ICON_BLACK,
        "Switch Flow Mode",
        build_menu(),
    )
    print("Switch Flow Mode 已啟動。系統托盤可見黑色圓形圖標。")
    print("點擊圖標 → 選模式 → Spotify 自動切歌。")
    print("（結束請從托盤選單按 ❌ 結束，或 Ctrl+C）")
    icon.run()


if __name__ == "__main__":
    main()
