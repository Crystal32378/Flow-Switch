#!/usr/bin/env python3
import json
import sys
import webbrowser
from pathlib import Path


BASE_DIR = Path(__file__).parent
MANUAL_CONFIG_PATH = BASE_DIR / "manual_playlists.json"

MODES = [
    ("focus", "專注", "ambient / 古典 / 純音樂"),
    ("push", "推進", "高能 J-Pop / K-Pop"),
    ("cinematic", "影視餘韻", "soundtrack / 史詩感配樂"),
    ("live", "現場戒斷", "Live 版本歌曲"),
]


def load_config() -> dict:
    if not MANUAL_CONFIG_PATH.exists():
        return {}
    with open(MANUAL_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: dict) -> None:
    with open(MANUAL_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write("\n")


def is_spotify_url(value: str) -> bool:
    return (
        value.startswith("https://open.spotify.com/")
        or value.startswith("spotify:")
    )


def setup() -> None:
    cfg = load_config()
    print("=" * 56)
    print("  Switch Flow Mode - 非 Premium 試玩設定")
    print("=" * 56)
    print()
    print("請先在 Spotify 建好 4 個 playlist，然後把連結貼進來。")
    print("如果某個模式暫時不想改，直接按 Enter 會保留原設定。")
    print()

    for key, label, hint in MODES:
        old = cfg.get(key, {}).get("url", "")
        if old:
            print(f"{label} 目前連結: {old}")
        print(f"{label} 建議內容: {hint}")
        while True:
            value = input(f"貼上 {label} playlist URL: ").strip()
            if not value and old:
                break
            if not value:
                print("  這個模式先留空。")
                cfg.pop(key, None)
                break
            if is_spotify_url(value):
                cfg[key] = {"label": label, "url": value, "hint": hint}
                break
            print("  看起來不像 Spotify 連結，請貼 open.spotify.com 或 spotify: 開頭的連結。")
        print()

    save_config(cfg)
    print("=" * 56)
    print(f"  已儲存到: {MANUAL_CONFIG_PATH}")
    print("  下一步：雙擊 5_manual_start.command 選模式試玩")
    print("=" * 56)


def start() -> None:
    cfg = load_config()
    ready = [(key, label, cfg[key]["url"]) for key, label, _ in MODES if key in cfg]
    if not ready:
        print("還沒有任何手動歌單設定。請先雙擊 4_manual_setup.command。")
        sys.exit(1)

    print("=" * 56)
    print("  Switch Flow Mode - 非 Premium 試玩")
    print("=" * 56)
    print()
    for idx, (_, label, url) in enumerate(ready, start=1):
        print(f"  {idx}. {label}  {url}")
    print()
    choice = input("選一個模式編號，或直接按 Enter 結束: ").strip()
    if not choice:
        return
    if not choice.isdigit() or not (1 <= int(choice) <= len(ready)):
        print("不認識的選項。")
        sys.exit(1)

    _, label, url = ready[int(choice) - 1]
    print(f"正在打開 Spotify：{label}")
    webbrowser.open(url)
    print("已送出打開請求。打開後請在 Spotify 裡手動按播放。")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"setup", "start"}:
        print("用法: python manual_flow.py setup|start")
        sys.exit(2)
    if sys.argv[1] == "setup":
        setup()
    else:
        start()


if __name__ == "__main__":
    main()
