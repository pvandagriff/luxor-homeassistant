"""Luxor API client."""
import logging
import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)


class LuxorController:
    """Luxor controller API client."""

    def __init__(self, host: str, session: aiohttp.ClientSession):
        """Initialize the Luxor controller."""
        self.host = host
        self.session = session
        # Make sure the URL is properly formatted without http:// if already included
        if host.startswith('http://') or host.startswith('https://'):
            self.base_url = host
        else:
            self.base_url = f"http://{host}"

    async def _request(self, method: str, extra_data: dict = None):
        """Make a request to the Luxor controller."""
        data = {"Method": method}
        if extra_data:
            data.update(extra_data)
        
        _LOGGER.debug("Requesting %s with data: %s", self.base_url, data)
        
        try:
            async with async_timeout.timeout(10):
                async with self.session.post(
                    self.base_url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    _LOGGER.debug("Response: %s", result)
                    return result
        except Exception as err:
            _LOGGER.error("Error connecting to Luxor controller at %s: %s", self.base_url, err)
            raise

    async def get_controller_name(self):
        """Get controller name and type."""
        return await self._request("ControllerName")

    def determine_controller_type(self, controller_info: dict) -> str:
        """Determine controller type from response."""
        controller_name = controller_info.get("Controller", "").lower()
        
        if "lxzdc" in controller_name:
            return "ZDC"
        elif "lxtwo" in controller_name:
            return "ZDTWO"
        else:
            return "ZD"

    async def get_group_list(self):
        """Get list of light groups."""
        response = await self._request("GroupListGet")
        return response.get("GroupList", [])

    async def get_theme_list(self):
        """Get list of themes."""
        response = await self._request("ThemeListGet")
        return response.get("ThemeList", [])

    async def illuminate_group(self, group_number: int, intensity: int):
        """Set group intensity (0-100)."""
        return await self._request("IlluminateGroup", {
            "GroupNumber": group_number,
            "Intensity": intensity
        })

    async def illuminate_theme(self, theme_index: int, on_off: int):
        """Activate a theme."""
        return await self._request("IlluminateTheme", {
            "ThemeIndex": theme_index,
            "OnOff": on_off
        })

    async def set_hue_sat(self, group_number: int, hue: int, sat: int):
        """Set hue and saturation for a color group."""
        return await self._request("SetHueSat", {
            "GroupNumber": group_number,
            "Hue": hue,
            "Sat": sat
        })
