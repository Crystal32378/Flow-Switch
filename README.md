# Flow Switch

Flow Switch is an independent Mac-first experiment for switching music listening modes.

The product idea is simple: each mode is a semantic entrance into a mood. The free MVP opens user-provided music links, and the music app can continue playback with its own native behavior.

This project is not affiliated with, endorsed by, or sponsored by Spotify. Spotify is mentioned only to describe compatibility with Spotify URLs and the Spotify Web API.

## Versions

| Version | Folder | Account requirement | Status |
| --- | --- | --- | --- |
| URL launcher MVP | `versions/url_launcher/` | Free account works for URL opening | Recommended MVP |
| Web API player control | `versions/spotipy_web_api/` | Usually requires Spotify Premium | Preserved for future use |
| AppleScript spike | `experiments/applescript_spike/` | Unknown | Diagnostic only |

## Recommended Start

Use `versions/url_launcher/` first:

1. Double-click `4_manual_setup.command`.
2. Paste four playlist or album URLs.
3. Double-click `5_manual_start.command`.
4. Pick a mode and play in your music app.

## Security

This repository must not contain real secrets.

Do not commit:

- `.env`
- `.spotify_cache.json`
- `spotify_app.json`
- `.venv/`
- `manual_playlists.json`

Use `.env.example` and `manual_playlists.example.json` as templates only.

If you accidentally committed a real Spotify client secret or token, rotate it immediately in the Spotify Developer Dashboard and remove it from git history.

## Branding

Do not use Spotify logos, icons, colors, or brand assets in this project. Do not present Flow Switch as an official Spotify product.
