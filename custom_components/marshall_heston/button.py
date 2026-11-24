"""Button entities (presets, pause) for the Marshall Heston integration."""

from collections.abc import Awaitable, Callable

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import HestonApi
from .const import DOMAIN, PRESETS
from .coordinator import HestonCoordinator
from .entity import HestonEntity

BUTTONS: tuple[
    tuple[ButtonEntityDescription, Callable[[HestonApi], Awaitable[None]]],
    ...,
] = (
    *(
        (
            ButtonEntityDescription(
                key=f"preset_{index}",
                translation_key=f"preset_{index}",
                icon=f"mdi:numeric-{index}-box",
            ),
            lambda api, index=index: api.play_preset(index),
        )
        for index in PRESETS
    ),
    (
        ButtonEntityDescription(key="pause", translation_key="pause", icon="mdi:pause"),
        lambda api: api.control_player("pause"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button entities."""
    coordinator: HestonCoordinator = hass.data[DOMAIN][entry.entry_id][1]
    async_add_entities(
        HestonButton(coordinator, entry, description, action)
        for description, action in BUTTONS
    )


class HestonButton(HestonEntity, ButtonEntity):
    """A button entity backed by the local Heston API."""

    def __init__(
        self,
        coordinator: HestonCoordinator,
        entry: ConfigEntry,
        description: ButtonEntityDescription,
        action: Callable[[HestonApi], Awaitable[None]],
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._action = action
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._action(self.coordinator.api)
        await self.coordinator.async_request_refresh()
