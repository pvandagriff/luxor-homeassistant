"""Config flow for Luxor integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_NAME_PREFIX
from .luxor_api import LuxorController

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME_PREFIX, default=""): cv.string,
})


class LuxorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Luxor."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            session = async_get_clientsession(self.hass)
            controller = LuxorController(host, session)

            try:
                controller_info = await controller.get_controller_name()
                controller_name = controller_info.get("Controller", "Unknown")
                
                await self.async_set_unique_id(controller_info.get("Controller"))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Luxor {controller_name}",
                    data=user_input,
                )
            except Exception as err:
                _LOGGER.error("Cannot connect to Luxor controller: %s", err)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )