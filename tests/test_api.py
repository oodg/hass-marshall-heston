"""Tests for the Heston API client."""

import re

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.marshall_heston.api import (
    HestonApi,
    HestonConnectionError,
    to_device_tone,
    to_ui_tone,
)

HOST = "192.168.1.50"
BASE = f"https://{HOST}:4430"


@pytest.fixture
async def api(hass):
    """Return an API client that is closed after the test."""
    client = HestonApi(HOST)
    yield client
    await client.close()


def test_tone_conversion() -> None:
    """Test the tone value conversion between UI and device scale."""
    assert to_device_tone(-6) == -12
    assert to_device_tone(3) == 3
    assert to_ui_tone(-12) == -6
    assert to_ui_tone(4) == 4.0


async def test_get_data_unwraps_list(hass, api) -> None:
    """Test that get_data returns the first element of a list response."""
    with aioresponses() as mocked:
        mocked.get(
            f"{BASE}/api/getData",
            payload=[{"type": "zappaPhysicalSource", "zappaPhysicalSource": "hdmieArc"}],
        )
        value = await api.get_data("settings:/zappa/physicalSource")
    assert value["zappaPhysicalSource"] == "hdmieArc"


async def test_async_get_state(hass, api) -> None:
    """Test that async_get_state maps the zappa responses to HestonState."""
    with aioresponses() as mocked:
        mocked.get(
            re.compile(rf"{BASE}/api/getData\?.*physicalSource"),
            payload=[{"zappaPhysicalSource": "bluetooth"}],
        )
        mocked.get(
            re.compile(rf"{BASE}/api/getData\?.*soundMode"),
            payload=[{"zappaSoundMode": "music"}],
        )
        mocked.get(
            re.compile(rf"{BASE}/api/getData\?.*player"),
            payload=[
                {
                    "state": "playing",
                    "trackRoles": {
                        "title": "Song",
                        "mediaData": {"metaData": {"artist": "Artist", "album": "Album"}},
                    },
                }
            ],
        )
        mocked.get(
            re.compile(rf"{BASE}/api/getData\?.*eqMusic"),
            payload=[
                {"zappaEqualizerValue": {"value1": -4, "value2": 0, "value3": 0, "value4": 0, "value5": 2}}
            ],
        )
        state = await api.async_get_state()
    assert state.source == "bluetooth"
    assert state.sound_mode == "music"
    assert state.bass == -2
    assert state.treble == 2
    assert state.player_state == "playing"
    assert state.title == "Song"
    assert state.artist == "Artist"
    assert state.album == "Album"


async def test_set_source_posts_payload(hass, api) -> None:
    """Test that set_source posts the expected setData payload."""
    with aioresponses() as mocked:
        mocked.post(f"{BASE}/api/setData", payload={"ok": True})
        await api.set_source("hdmi")
        request = next(iter(mocked.requests.values()))[0]
    assert request.kwargs["json"] == {
        "path": "settings:/zappa/physicalSource",
        "role": "value",
        "value": {"type": "zappaPhysicalSource", "zappaPhysicalSource": "hdmi"},
    }


async def test_connection_error(hass, api) -> None:
    """Test that connection problems raise HestonConnectionError."""
    with aioresponses() as mocked:
        mocked.get(
            re.compile(r"/api/getData"),
            exception=aiohttp.ClientConnectionError("boom"),
        )
        with pytest.raises(HestonConnectionError):
            await api.get_data("zappa:soundMode")
