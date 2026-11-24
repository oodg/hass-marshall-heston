"""Select entities for the Marshall Heston integration."""

from collections.abc import Awaitable, Callable

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import HestonApi, HestonState
from .const import DOMAIN, SOUND_MODES, SOURCES
from .coordinator import HestonCoordinator
from .entity import HestonEntity

SELECTS: tuple[
    tuple[
        SelectEntityDescription,
        Callable[[HestonState], str | None],
        Callable[[HestonApi, str], Awaitable[None]],
    ],
    ...,
] = (
    (
        SelectEntityDescription(key="source", translation_key="source", options=SOURCES),
        lambda state: state.source,
        lambda api, option: api.set_source(option),
    ),
    (
        SelectEntityDescription(key="sound_mode", translation_key="sound_mode", options=SOUND_MODES),
        lambda state: state.sound_mode,
        lambda api, option: api.set_sound_mode(option),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select entities."""
    coordinator: HestonCoordinator = hass.data[DOMAIN][entry.entry_id][1]
    async_add_entities(
        HestonSelect(coordinator, entry, description, current, setter)
        for description, current, setter in SELECTS
    )


class HestonSelect(HestonEntity, SelectEntity):
    """A select entity backed by the local Heston API."""

    def __init__(
        self,
        coordinator: HestonCoordinator,
        entry: ConfigEntry,
        description: SelectEntityDescription,
        current: Callable[[HestonState], str | None],
        setter: Callable[[HestonApi, str], Awaitable[None]],
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._current = current
        self._setter = setter
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        return self._current(self.coordinator.data)

    async def async_select_option(self, option: str) -> None:
        """Change the option."""
        await self._setter(self.coordinator.api, option)
        await self.coordinator.async_request_refresh()
