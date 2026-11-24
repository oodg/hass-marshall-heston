"""Tests for the Marshall Heston config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.marshall_heston.api import HestonConnectionError, HestonState
from custom_components.marshall_heston.const import DOMAIN

HOST = "192.168.1.50"


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    """Test a successful user flow."""
    with patch("custom_components.marshall_heston.config_flow.HestonApi") as api_cls:
        api_cls.return_value.async_get_state = AsyncMock(return_value=HestonState(source="wifi"))
        api_cls.return_value.close = AsyncMock()
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data={CONF_HOST: HOST}
        )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == HOST
    assert result["data"] == {CONF_HOST: HOST}


async def test_user_flow_cannot_connect(hass: HomeAssistant) -> None:
    """Test the error handling when the soundbar is unreachable."""
    with patch("custom_components.marshall_heston.config_flow.HestonApi") as api_cls:
        api_cls.return_value.async_get_state = AsyncMock(
            side_effect=HestonConnectionError("nope")
        )
        api_cls.return_value.close = AsyncMock()
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data={CONF_HOST: HOST}
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
