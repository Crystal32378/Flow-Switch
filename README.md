# Flow Switch

Flow Switch is a small Mac-first experiment for changing Spotify listening modes.

The product idea is simple: each mode is a semantic entrance into a mood. Spotify can then continue the flow with its own app behavior.

## Versions

| Version | Folder | Account requirement | Status |
| --- | --- | --- | --- |
| C. URL launcher | `C_url_launcher_version/` | Free Spotify works | Recommended MVP |
| A. Spotipy player control | `A_spotipy_version/` | Usually requires Spotify Premium | Preserved for future use |
| B. AppleScript spike | `B_applescript_spike/` | Unknown | Diagnostic only |

## Recommended Start

Use `C_url_launcher_version/` first:

1. Double-click `4_manual_setup.command`.
2. Paste four Spotify playlist or album URLs.
3. Double-click `5_manual_start.command`.
4. Pick a mode and play in Spotify.

## Security

This repository must not contain real secrets.

Do not commit:

- `.env`
- `.spotify_cache.json`
- `spotify_app.json`
- `.venv/`
- `manual_playlists.json`

Use `.env.example` and `manual_playlists.example.json` as templates only.
