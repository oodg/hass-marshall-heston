"""Sensor entities for the Marshall Heston integration."""

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HestonCoordinator
from .entity import HestonEntity

PLAYER_SENSOR = SensorEntityDescription(
    key="player",
    translation_key="player",
    icon="mdi:play-circle-outline",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor entities."""
    coordinator: HestonCoordinator = hass.data[DOMAIN][entry.entry_id][1]
    async_add_entities([HestonPlayerSensor(coordinator, entry, PLAYER_SENSOR)])


class HestonPlayerSensor(HestonEntity, SensorEntity):
    """Sensor exposing the player state and current track."""

    def __init__(
        self,
        coordinator: HestonCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> str | None:
        """Return the player state."""
        return self.coordinator.data.player_state

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the current track metadata."""
        data = self.coordinator.data
        return {"title": data.title, "artist": data.artist, "album": data.album}
