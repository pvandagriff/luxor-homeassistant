"""Luxor light platform."""
import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_HS_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, GROUP_TYPE_MONO, GROUP_TYPE_COLOR

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luxor lights from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    controller = data["controller"]
    coordinator = data["coordinator"]
    name_prefix = data["name_prefix"]
    controller_type = data["controller_type"]

    entities = []
    
    if coordinator.data and "groups" in coordinator.data:
        for group in coordinator.data["groups"]:
            # Colr: 1 = monochrome, 2 = color
            group_type = group.get("Colr", 1)
            
            if group_type == GROUP_TYPE_COLOR and controller_type in ["ZDC", "ZDTWO"]:
                entities.append(LuxorColorLight(coordinator, controller, group, name_prefix))
            else:
                entities.append(LuxorLight(coordinator, controller, group, name_prefix))

    async_add_entities(entities)


class LuxorLight(CoordinatorEntity, LightEntity):
    """Representation of a Luxor monochrome light group."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, coordinator, controller, group_data, name_prefix):
        """Initialize the light."""
        super().__init__(coordinator)
        self._controller = controller
        self._group_data = group_data
        self._group_number = group_data["Grp"]
        self._name_prefix = name_prefix
        
        self._attr_name = f"{name_prefix}{group_data['Name']}"
        self._attr_unique_id = f"luxor_{controller.host}_{self._group_number}"

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        if self.coordinator.data and "groups" in self.coordinator.data:
            for group in self.coordinator.data["groups"]:
                if group["Grp"] == self._group_number:
                    return group.get("Inten", 0) > 0
        return False

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        if self.coordinator.data and "groups" in self.coordinator.data:
            for group in self.coordinator.data["groups"]:
                if group["Grp"] == self._group_number:
                    intensity = group.get("Inten", 0)
                    return int(intensity * 255 / 100)
        return 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        intensity = int(brightness * 100 / 255)
        
        await self._controller.illuminate_group(self._group_number, intensity)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self._controller.illuminate_group(self._group_number, 0)
        await self.coordinator.async_request_refresh()


class LuxorColorLight(LuxorLight):
    """Representation of a Luxor color light group."""

    _attr_color_mode = ColorMode.HS
    _attr_supported_color_modes = {ColorMode.HS}

    def __init__(self, coordinator, controller, group_data, name_prefix):
        """Initialize the color light."""
        super().__init__(coordinator, controller, group_data, name_prefix)

    @property
    def hs_color(self) -> tuple[float, float]:
        """Return the hue and saturation color value."""
        if self.coordinator.data and "groups" in self.coordinator.data:
            for group in self.coordinator.data["groups"]:
                if group["Grp"] == self._group_number:
                    hue = group.get("Hue", 0)
                    sat = group.get("Sat", 0)
                    return (hue, sat)
        return (0, 0)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if ATTR_HS_COLOR in kwargs:
            hue, sat = kwargs[ATTR_HS_COLOR]
            await self._controller.set_hue_sat(
                self._group_number,
                int(hue),
                int(sat)
            )
        
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
            intensity = int(brightness * 100 / 255)
            await self._controller.illuminate_group(self._group_number, intensity)
        elif ATTR_HS_COLOR not in kwargs:
            await self._controller.illuminate_group(self._group_number, 100)
        
        await self.coordinator.async_request_refresh()
