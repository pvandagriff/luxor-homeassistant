"""Luxor Lighting integration for Home Assistant."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_HOST, Platform

from .const import DOMAIN, CONF_NAME_PREFIX
from .luxor_api import LuxorController

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.LIGHT, Platform.BUTTON]
SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Luxor from a config entry."""
    host = entry.data[CONF_HOST]
    name_prefix = entry.data.get(CONF_NAME_PREFIX, "")
    
    session = async_get_clientsession(hass)
    controller = LuxorController(host, session)
    
    try:
        controller_info = await controller.get_controller_name()
        controller_type = controller.determine_controller_type(controller_info)
    except Exception as err:
        _LOGGER.error("Failed to connect to Luxor controller at %s: %s", host, err)
        return False
    
    async def async_update_data():
        """Fetch data from Luxor controller."""
        try:
            group_list = await controller.get_group_list()
            theme_list = await controller.get_theme_list()
            return {
                "groups": group_list,
                "themes": theme_list,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Luxor controller: {err}")
    
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"luxor_{host}",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "controller": controller,
        "coordinator": coordinator,
        "controller_type": controller_type,
        "controller_info": controller_info,
        "name_prefix": name_prefix,
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok