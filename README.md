# Marshall Heston for Home Assistant

Custom integration (HACS) for **local** control of a Marshall Heston soundbar (Heston 60 / 100 / 120) via its HTTPS API on **port 4430**.

Volume, mute and casting are intentionally **not** handled by this integration – the built-in **Google Cast** integration (`cast`) in Home Assistant takes care of that and automatically detects the Heston as a `media_player`.

## Features

- **Source** selection (`select`): HDMI eARC, HDMI, RCA, Optical, AUX, Bluetooth, Wi-Fi
- **Sound mode** (`select`): Music, Movie, Night, Voice
- **Bass / treble** (`number`, -6 to +6) of the active sound mode
- **Presets 1–3** (`button`, configured in the Marshall app)
- **Pause** (`button`)
- **Player status** incl. title/artist/album (`sensor`)
- Automatic discovery in the local network (mDNS `_googlecast._tcp`, device name contains "Heston"/"Marshall") or manual IP entry

## Installation

### HACS (recommended)

1. HACS → ⋮ → "Custom repositories" → add `https://github.com/oodg/hass-marshall-heston`, category **Integration**
2. Download "Marshall Heston" and restart Home Assistant

### Manual

Copy the `custom_components/marshall_heston/` directory into the `custom_components/` directory of your Home Assistant configuration and restart.

## Setup

Settings → Devices & services → "Add integration" → **Marshall Heston**. The soundbar is discovered automatically when it is reachable in the same network with "Heston" in its device name; alternatively enter the IP address manually.

## Technical background

The soundbar exposes a local HTTPS API with a self-signed certificate on port 4430:

- `GET /api/getData?path=<path>&roles=value` → read a value from the "zappa" tree
- `POST /api/setData` with `{"path": ..., "role": "value"|"activate", "value": {...}}` → set a value

Paths used:

| Function | Path |
|---|---|
| Read/set source | `settings:/zappa/physicalSource` |
| Read sound mode | `zappa:soundMode` |
| Set sound mode | `zappa:soundMode/request` (role `activate`) |
| EQ per mode | `settings:/zappa/audio/eqMusic` / `eqMovie` / `eqNight` / `eqVoice` (`value1` = bass, `value5` = treble; negative device values = 2× UI value) |
| Player status | `player:player/data` |
| Player control | `player:player/control` (role `activate`) |
| Play preset | `zappa:presets/play?id=1..3` (role `activate`) |

Reference implementation: [andreasvikke/marshall-speaker](https://github.com/andreasvikke/marshall-speaker) (Homey app, `managers/heston-api-manager.js`).

## Notes

- There is no real power-off; after the idle timeout the Heston goes into network standby and wakes up e.g. via TV (HDMI-CEC), Cast or the Marshall app.
- Presets require the soundbar to have internet access.
- The 4430 API is undocumented and may change with firmware updates.
- Unofficial project; not affiliated with Marshall PLC.

## Development

```bash
pip install -r tests/requirements_test.txt
pytest tests/
```
