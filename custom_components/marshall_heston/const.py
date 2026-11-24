"""Constants for the Marshall Heston integration."""

from typing import Final

DOMAIN: Final = "marshall_heston"

API_PORT: Final = 4430
API_TIMEOUT: Final = 10
SCAN_INTERVAL_SECONDS: Final = 30

PATH_PHYSICAL_SOURCE: Final = "settings:/zappa/physicalSource"
PATH_SOUND_MODE: Final = "zappa:soundMode"
PATH_SOUND_MODE_REQUEST: Final = "zappa:soundMode/request"
PATH_PLAYER_DATA: Final = "player:player/data"
PATH_PLAYER_CONTROL: Final = "player:player/control"
PATH_PRESET_PLAY: Final = "zappa:presets/play?id={index}"

EQ_PATHS: Final[dict[str, str]] = {
    "movie": "settings:/zappa/audio/eqMovie",
    "music": "settings:/zappa/audio/eqMusic",
    "night": "settings:/zappa/audio/eqNight",
    "voice": "settings:/zappa/audio/eqVoice",
}

SOURCES: Final[list[str]] = ["hdmieArc", "hdmi", "rca", "optical", "aux", "bluetooth", "wifi"]
SOUND_MODES: Final[list[str]] = ["music", "movie", "night", "voice"]
PRESETS: Final[list[int]] = [1, 2, 3]

EQ_BAND_COUNT: Final = 5
EQ_BASS_KEY: Final = "value1"
EQ_TREBLE_KEY: Final = "value5"

TONE_MIN: Final = -6
TONE_MAX: Final = 6
