"""Base entity for the Marshall Heston integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HestonCoordinator


class HestonEntity(CoordinatorEntity[HestonCoordinator]):
    """Base class for all Marshall Heston entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HestonCoordinator, entry: ConfigEntry) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.data[CONF_HOST])},
            name=entry.title,
            manufacturer="Marshall",
            model="Heston",
        )
