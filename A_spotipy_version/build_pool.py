"""
build_pool.py — Track Pool 建立 helper

Spotify 2024/11/27 後新 app 無法使用 recommendations API，
Switch Flow Mode 改用本地 track pool。這個 helper 幫你從自己的
playlist 抓曲目，自動寫入 config.json 對應的模式欄位。

前置條件：
  1. 已執行 python get_token.py 完成授權
  2. config.json 存在

用法：
  # 列出你所有的 playlist（名稱 + ID + URL + 曲目數）
  python build_pool.py list

  # 從某個 playlist 抓所有曲目，寫入 config.json 的 push_tracks 欄位
  python build_pool.py pull "https://open.spotify.com/playlist/37i9dQZF1DX..." push

  # 不寫入 config.json，只把曲目 URI 印出來
  python build_pool.py pull "https://...playlist/xxx" focus --dry-run

可用的 mode 名稱（對應 config.json 欄位）：
  focus       -> focus_tracks
  push        -> push_tracks
  cinematic   -> cinematic_tracks
  live        -> live_tracks
"""

import argparse
import json
import sys
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotify_auth import CACHE_PATH, REDIRECT_URI, SCOPES, load_spotify_settings

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"

# mode 名稱 -> config.json 欄位
MODE_TO_KEY = {
    "focus": "focus_tracks",
    "push": "push_tracks",
    "cinematic": "cinematic_tracks",
    "live": "live_tracks",
}


def get_spotify() -> spotipy.Spotify:
    if not CACHE_PATH.exists():
        print("找不到 .spotify_cache.json，請先執行: python get_token.py", file=sys.stderr)
        sys.exit(1)
    try:
        client_id, client_secret = load_spotify_settings()
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    auth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_path=str(CACHE_PATH),
    )
    return spotipy.Spotify(auth_manager=auth)


def parse_playlist_id(s: str) -> str:
    """接受 playlist URI / URL / 純 ID，回傳純 ID。"""
    s = s.strip()
    if s.startswith("spotify:playlist:"):
        return s.split(":")[-1]
    if "open.spotify.com/playlist/" in s:
        return s.split("/playlist/")[-1].split("?")[0]
    return s


def cmd_list(sp: spotipy.Spotify) -> None:
    print("正在抓取你的所有 playlist...\n")
    results = sp.current_user_playlists(limit=50)
    playlists = results.get("items", [])
    while results.get("next"):
        results = sp.next(results)
        playlists.extend(results.get("items", []))

    if not playlists:
        print("你沒有任何 playlist。")
        return

    print(f"{'名稱':<32} {'曲目數':>6}  URL")
    print("-" * 90)
    for p in playlists:
        name = p.get("name", "(未命名)")[:30]
        n = p.get("tracks", {}).get("total", 0)
        url = p.get("external_urls", {}).get("spotify", "")
        print(f"{name:<32} {n:>6}  {url}")

    print(f"\n共 {len(playlists)} 個 playlist。")
    print("\n下一步：")
    print("  python build_pool.py pull \"<上方任一 playlist URL>\" <mode>")
    print("  mode 可選: focus / push / cinematic / live")


def fetch_all_tracks(sp: spotipy.Spotify, playlist_id: str) -> list[str]:
    """抓 playlist 內所有 track URI（自動分頁、過濾 local track 與非 track item）。"""
    uris: list[str] = []
    results = sp.playlist_items(playlist_id, limit=100, additional_types=("track",))
    while True:
        for item in results.get("items", []):
            track = item.get("track")
            if not track:
                continue
            if track.get("is_local"):
                continue  # 本機檔案沒有 URI 可播
            uri = track.get("uri", "")
            if uri.startswith("spotify:track:"):
                uris.append(uri)
        if not results.get("next"):
            break
        results = sp.next(results)
    return uris


def cmd_pull(sp: spotipy.Spotify, playlist_ref: str, mode: str, dry_run: bool) -> None:
    if mode not in MODE_TO_KEY:
        print(f"未知 mode: {mode}", file=sys.stderr)
        print(f"可用 mode: {', '.join(MODE_TO_KEY.keys())}", file=sys.stderr)
        sys.exit(2)

    playlist_id = parse_playlist_id(playlist_ref)

    # 抓 playlist metadata 顯示名稱
    try:
        meta = sp.playlist(playlist_id, fields="name,owner(display_name),tracks(total)")
    except Exception as e:
        print(f"讀取 playlist 失敗: {e}", file=sys.stderr)
        sys.exit(1)

    pl_name = meta.get("name", "(未知)")
    owner = meta.get("owner", {}).get("display_name", "?")
    total = meta.get("tracks", {}).get("total", 0)
    print(f"Playlist: {pl_name}  (owner: {owner}, 共 {total} 首)")

    print("正在抓取所有曲目...")
    uris = fetch_all_tracks(sp, playlist_id)
    print(f"✓ 取得 {len(uris)} 個有效 Track URI（已過濾 local track）")

    if not uris:
        print("這個 playlist 沒有可用的曲目。", file=sys.stderr)
        sys.exit(1)

    if dry_run:
        print("\n--- URI 清單（dry-run，未寫入 config.json）---")
        for u in uris:
            print(u)
        return

    # 寫入 config.json
    if not CONFIG_PATH.exists():
        print(f"找不到 {CONFIG_PATH}，請先建立（參考 README）", file=sys.stderr)
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    key = MODE_TO_KEY[mode]
    old_count = len(cfg.get(key, []))
    cfg[key] = uris

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 已寫入 config.json 的 {key} 欄位")
    print(f"   原本: {old_count} 首  →  現在: {len(uris)} 首")
    print(f"   來源 playlist: {pl_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Switch Flow Mode — Track Pool 建立 helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="列出你所有的 playlist")

    p_pull = sub.add_parser("pull", help="從 playlist 抓曲目寫入 config.json")
    p_pull.add_argument("playlist", help="playlist URL / URI / ID")
    p_pull.add_argument("mode", choices=list(MODE_TO_KEY.keys()),
                        help="要寫入的模式 (focus/push/cinematic/live)")
    p_pull.add_argument("--dry-run", action="store_true",
                        help="只印 URI 不寫入 config.json")

    args = parser.parse_args()

    sp = get_spotify()
    if args.cmd == "list":
        cmd_list(sp)
    elif args.cmd == "pull":
        cmd_pull(sp, args.playlist, args.mode, args.dry_run)


if __name__ == "__main__":
    main()
