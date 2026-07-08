import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"
CACHE_PATH = BASE_DIR / ".spotify_cache.json"

REDIRECT_URI = "http://127.0.0.1:8888/callback"

SCOPES = " ".join([
    "user-modify-playback-state",
    "user-read-playback-state",
    "user-read-currently-playing",
    "streaming",
    "playlist-read-private",
    "playlist-read-collaborative",
])


def load_spotify_settings() -> tuple[str, str]:
    load_dotenv(ENV_PATH)
    client_id = os.environ.get("SPOTIFY_CLIENT_ID", "").strip()
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "").strip()

    if client_id and client_secret:
        return client_id, client_secret

    raise RuntimeError(
        "找不到 Spotify App 設定。請複製 .env.example 為 .env，"
        "並填入 SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET。"
    )
