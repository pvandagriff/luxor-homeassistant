"""Luxor theme button platform."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luxor theme buttons from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    controller = data["controller"]
    coordinator = data["coordinator"]
    name_prefix = data["name_prefix"]

    entities = []
    
    if coordinator.data and "themes" in coordinator.data:
        for theme in coordinator.data["themes"]:
            entities.append(LuxorThemeButton(coordinator, controller, theme, name_prefix))

    async_add_entities(entities)


class LuxorThemeButton(CoordinatorEntity, ButtonEntity):
    """Representation of a Luxor theme as a button."""

    def __init__(self, coordinator, controller, theme_data, name_prefix):
        """Initialize the button."""
        super().__init__(coordinator)
        self._controller = controller
        self._theme_data = theme_data
        self._theme_index = theme_data["ThemeIndex"]
        self._name_prefix = name_prefix
        
        self._attr_name = f"{name_prefix}{theme_data['Name']}"
        self._attr_unique_id = f"luxor_{controller.host}_theme_{self._theme_index}"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._controller.illuminate_theme(self._theme_index, 1)
        await self.coordinator.async_request_refresh()