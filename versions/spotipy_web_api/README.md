# Spotipy Web API Player Control

This is the Web API player-control version.

It uses the Spotify Web API through `spotipy`, so Spotify may require a Premium account for playback commands.

This project is not affiliated with, endorsed by, or sponsored by Spotify. Spotify is mentioned only to describe API compatibility.

## Setup

1. Create a Spotify app in the Spotify Developer Dashboard.
2. Add this Redirect URI:

```text
http://127.0.0.1:8888/callback
```

3. Copy `.env.example` to `.env`.
4. Fill in:

```text
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
```

5. Run `1_setup.command`.

Never commit `.env`, `.spotify_cache.json`, or `.venv/`.
