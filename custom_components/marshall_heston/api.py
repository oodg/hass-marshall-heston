"""Async client for the local API of a Marshall Heston soundbar (port 4430)."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

import aiohttp

from .const import (
    API_PORT,
    API_TIMEOUT,
    EQ_BAND_COUNT,
    EQ_BASS_KEY,
    EQ_PATHS,
    EQ_TREBLE_KEY,
    PATH_PHYSICAL_SOURCE,
    PATH_PLAYER_CONTROL,
    PATH_PLAYER_DATA,
    PATH_PRESET_PLAY,
    PATH_SOUND_MODE,
    PATH_SOUND_MODE_REQUEST,
)


class HestonApiError(Exception):
    """Error returned by the Heston API."""


class HestonConnectionError(HestonApiError):
    """The soundbar could not be reached."""


@dataclass
class HestonState:
    """State of the soundbar as reported by the local API."""

    source: str | None = None
    sound_mode: str | None = None
    bass: float = 0
    treble: float = 0
    player_state: str | None = None
    title: str = ""
    artist: str = ""
    album: str = ""


def to_device_tone(value: float) -> int:
    """Convert a UI tone value to the raw device value."""
    return int(value * 2) if value < 0 else int(value)


def to_ui_tone(value: int) -> float:
    """Convert a raw device tone value to a UI value."""
    return value / 2 if value < 0 else float(value)


class HestonApi:
    """Client for the local HTTPS API ("zappa" API) of a Marshall Heston soundbar."""

    def __init__(self, host: str) -> None:
        """Initialize the client. The API uses a self-signed certificate, so SSL verification is disabled."""
        self._host = host
        self._base_url = f"https://{host}:{API_PORT}"
        self._lock = asyncio.Lock()
        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False),
            timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
        )

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        await self._session.close()

    async def _request(
        self,
        path: str,
        *,
        method: str = "GET",
        params: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        try:
            async with self._session.request(
                method, f"{self._base_url}{path}", params=params, json=payload
            ) as resp:
                text = await resp.text()
                body: Any = None
                if text:
                    try:
                        body = json.loads(text)
                    except json.JSONDecodeError:
                        body = text
                if not resp.ok:
                    message = None
                    if isinstance(body, dict):
                        error = body.get("error")
                        if isinstance(error, dict):
                            message = error.get("message")
                    raise HestonApiError(message or f"HTTP {resp.status} for {path}")
                return body
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise HestonConnectionError(f"Cannot reach Heston at {self._host}: {err}") from err

    async def get_data(self, path: str, role: str = "value") -> Any:
        """Read a value from the zappa tree."""
        body = await self._request("/api/getData", params={"path": path, "roles": role})
        if isinstance(body, list):
            return body[0] if body else None
        return body

    async def _set_data(self, path: str, role: str, value: dict[str, Any]) -> Any:
        return await self._request(
            "/api/setData", method="POST", payload={"path": path, "role": role, "value": value}
        )

    async def async_get_state(self) -> HestonState:
        """Fetch source, sound mode, EQ and player state in one pass."""
        source_raw, mode_raw, player_raw = await asyncio.gather(
            self.get_data(PATH_PHYSICAL_SOURCE),
            self.get_data(PATH_SOUND_MODE),
            self.get_data(PATH_PLAYER_DATA),
        )
        sound_mode = (mode_raw or {}).get("zappaSoundMode")
        equalizer: dict[str, Any] = {}
        if sound_mode in EQ_PATHS:
            eq_raw = await self.get_data(EQ_PATHS[sound_mode])
            equalizer = (eq_raw or {}).get("zappaEqualizerValue") or {}
        player = player_raw or {}
        track = player.get("trackRoles") or {}
        metadata = (track.get("mediaData") or {}).get("metaData") or {}
        return HestonState(
            source=(source_raw or {}).get("zappaPhysicalSource"),
            sound_mode=sound_mode,
            bass=to_ui_tone(int(equalizer.get(EQ_BASS_KEY, 0) or 0)),
            treble=to_ui_tone(int(equalizer.get(EQ_TREBLE_KEY, 0) or 0)),
            player_state=player.get("state"),
            title=track.get("title") or (player.get("mediaRoles") or {}).get("title") or "",
            artist=metadata.get("artist", ""),
            album=metadata.get("album", ""),
        )

    async def set_source(self, source: str) -> None:
        """Set the physical input source."""
        async with self._lock:
            await self._set_data(
                PATH_PHYSICAL_SOURCE,
                "value",
                {"type": "zappaPhysicalSource", "zappaPhysicalSource": source},
            )

    async def set_sound_mode(self, mode: str) -> None:
        """Activate a sound mode (music, movie, night, voice)."""
        if mode not in EQ_PATHS:
            raise HestonApiError(f"Unsupported sound mode: {mode}")
        async with self._lock:
            await self._set_data(
                PATH_SOUND_MODE_REQUEST,
                "activate",
                {"type": "zappaSoundMode", "zappaSoundMode": mode},
            )

    async def get_equalizer(self, mode: str) -> dict[str, Any]:
        """Read the 5-band EQ of a sound mode."""
        raw = await self.get_data(EQ_PATHS[mode])
        return (raw or {}).get("zappaEqualizerValue") or {}

    async def set_tone(self, band: str, value: float) -> None:
        """Set bass or treble, preserving the other EQ bands of the active sound mode."""
        async with self._lock:
            mode_raw = await self.get_data(PATH_SOUND_MODE)
            mode = (mode_raw or {}).get("zappaSoundMode")
            if mode not in EQ_PATHS:
                raise HestonApiError(f"Unsupported sound mode: {mode}")
            current = await self.get_equalizer(mode)
            equalizer = {
                f"value{index}": int(current.get(f"value{index}", 0) or 0)
                for index in range(1, EQ_BAND_COUNT + 1)
            }
            equalizer[EQ_BASS_KEY if band == "bass" else EQ_TREBLE_KEY] = to_device_tone(value)
            await self._set_data(
                EQ_PATHS[mode],
                "value",
                {"type": "zappaEqualizerValue", "zappaEqualizerValue": equalizer},
            )

    async def play_preset(self, index: int) -> None:
        """Play a preset (1-3) configured in the Marshall app."""
        async with self._lock:
            await self._set_data(PATH_PRESET_PLAY.format(index=index), "activate", {})

    async def control_player(self, control: str) -> None:
        """Send a player control command (e.g. pause, play)."""
        async with self._lock:
            await self._set_data(PATH_PLAYER_CONTROL, "activate", {"control": control})
