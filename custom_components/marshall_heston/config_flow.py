"""Config flow for the Marshall Heston integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .api import HestonApi, HestonApiError, HestonConnectionError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

HOST_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


async def _async_validate_input(hass: HomeAssistant, host: str) -> None:
    api = HestonApi(host)
    try:
        await api.async_get_state()
    finally:
        await api.close()


class HestonConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Marshall Heston."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None
        self._name: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step where the user enters the host."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                await _async_validate_input(self.hass, host)
            except HestonConnectionError:
                errors["base"] = "cannot_connect"
            except HestonApiError:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(title=host, data={CONF_HOST: host})
        return self.async_show_form(step_id="user", data_schema=HOST_SCHEMA, errors=errors)

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle a discovered Google Cast device and check whether it is a Heston."""
        if discovery_info.type != "_googlecast._tcp.local.":
            return self.async_abort(reason="not_heston")
        name = (discovery_info.name or "").lower()
        if "heston" not in name and "marshall" not in name:
            return self.async_abort(reason="not_heston")
        self._host = discovery_info.host
        self._name = (discovery_info.name or "").split(".")[0]
        await self.async_set_unique_id(discovery_info.properties.get("id") or self._host)
        self._abort_if_unique_id_configured(updates={CONF_HOST: self._host})
        self.context.update({"title_placeholders": {"name": self._name}})
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm the discovered device."""
        if user_input is not None:
            try:
                await _async_validate_input(self.hass, self._host)
            except HestonConnectionError:
                return self.async_abort(reason="cannot_connect")
            except HestonApiError:
                return self.async_abort(reason="unknown")
            return self.async_create_entry(
                title=self._name or self._host, data={CONF_HOST: self._host}
            )
        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={"name": self._name or ""},
        )
