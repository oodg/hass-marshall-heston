"""Data update coordinator for the Marshall Heston integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HestonApi, HestonApiError, HestonState
from .const import DOMAIN, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class HestonCoordinator(DataUpdateCoordinator[HestonState]):
    """Coordinator polling the local Heston API."""

    def __init__(self, hass: HomeAssistant, api: HestonApi) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.api = api

    async def _async_update_data(self) -> HestonState:
        """Fetch the latest state from the soundbar."""
        try:
            return await self.api.async_get_state()
        except HestonApiError as err:
            raise UpdateFailed(f"Error communicating with Heston: {err}") from err
