# Flow Switch

Flow Switch is an independent Mac-first experiment for switching music listening modes.

The product idea is simple: each mode is a semantic entrance into a mood. The free MVP opens user-provided music service links, and the music app can continue playback with its own native behavior.

This project is not affiliated with, endorsed by, or sponsored by Spotify. Spotify is mentioned only to describe compatibility with Spotify URLs and the Spotify Web API.

## Versions

| Version | Folder | Account requirement | Status |
| --- | --- | --- | --- |
| C. URL launcher | `C_url_launcher_version/` | Free account works for URL opening | Recommended MVP |
| A. Web API player control | `A_spotipy_version/` | Usually requires Spotify Premium | Preserved for future use |
| B. AppleScript spike | `B_applescript_spike/` | Unknown | Diagnostic only |

## Recommended Start

Use `C_url_launcher_version/` first:

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

## Branding

Do not use Spotify logos, icons, colors, or brand assets in this project. Do not present Flow Switch as an official Spotify product.
