"""
get_token.py — 一次性執行的 Spotify 授權腳本

說明：
  Spotify 的 access_token 1 小時就過期，不能直接寫死在主程式裡。
  這個腳本跑一次，會把 refresh_token 存到 .spotify_cache.json，
  之後 flow_switcher.py 會自動用它換新的 access_token。
  等同於「跑一次永久用」，符合 MVP 自用精神。

使用流程：
  1. 到 https://developer.spotify.com/dashboard 建立 App
  2. 複製 .env.example 為 .env，填入 CLIENT_ID / CLIENT_SECRET
  3. Redirect URI 設為 http://127.0.0.1:8888/callback
  4. 執行: python get_token.py
  5. 瀏覽器會跳出 Spotify 授權頁，同意即可
  6. 看到 ✅ 訊息就完成了，接著去執行 flow_switcher.py
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotify_auth import CACHE_PATH, REDIRECT_URI, SCOPES, load_spotify_settings


def main():
    try:
        client_id, client_secret = load_spotify_settings()
    except RuntimeError as e:
        print("=" * 56)
        print(f"  {e}")
        print("  建立 Spotify App: https://developer.spotify.com/dashboard")
        print("  請複製 .env.example 為 .env，並填入你的 Spotify App 金鑰")
        print("  Redirect URI 設為: http://127.0.0.1:8888/callback")
        print("=" * 56)
        return

    print("啟動 Spotify 授權流程...")
    print("（若瀏覽器沒自動開啟，請手動複製下方的 URL 貼到瀏覽器）\n")

    auth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_path=str(CACHE_PATH),
        open_browser=True,
    )

    # 觸發授權流程；若 cache 已存在且有效則直接回傳。
    # spotipy 2.26 的 get_access_token 不再接受 prompt_for_browser 參數。
    token_info = auth.get_access_token()

    sp = spotipy.Spotify(auth=token_info["access_token"])
    user = sp.current_user()
    print()
    print("=" * 56)
    print(f"  ✅ 授權成功！使用者: {user.get('display_name', user.get('id'))}")
    print(f"  📁 Token cache 已儲存到: {CACHE_PATH}")
    print()
    print("  下一步:")
    print("    1. 跑 python build_pool.py 從你的 playlist 抓曲目填入 config.json")
    print("       (或手動編輯 config.json)")
    print("    2. python flow_switcher.py 啟動托盤小工具")
    print("=" * 56)


if __name__ == "__main__":
    main()
