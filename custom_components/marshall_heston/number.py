"""Number entities (bass/treble) for the Marshall Heston integration."""

from collections.abc import Callable

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import HestonState
from .const import DOMAIN, TONE_MAX, TONE_MIN
from .coordinator import HestonCoordinator
from .entity import HestonEntity

TONES: tuple[
    tuple[NumberEntityDescription, str, Callable[[HestonState], float]],
    ...,
] = (
    (
        NumberEntityDescription(key="bass", translation_key="bass"),
        "bass",
        lambda state: state.bass,
    ),
    (
        NumberEntityDescription(key="treble", translation_key="treble"),
        "treble",
        lambda state: state.treble,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number entities."""
    coordinator: HestonCoordinator = hass.data[DOMAIN][entry.entry_id][1]
    async_add_entities(
        HestonToneNumber(coordinator, entry, description, band, current)
        for description, band, current in TONES
    )


class HestonToneNumber(HestonEntity, NumberEntity):
    """A bass/treble slider backed by the EQ of the active sound mode."""

    _attr_native_min_value = TONE_MIN
    _attr_native_max_value = TONE_MAX
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: HestonCoordinator,
        entry: ConfigEntry,
        description: NumberEntityDescription,
        band: str,
        current: Callable[[HestonState], float],
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._band = band
        self._current = current
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._current(self.coordinator.data)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        await self.coordinator.api.set_tone(self._band, value)
        await self.coordinator.async_request_refresh()
