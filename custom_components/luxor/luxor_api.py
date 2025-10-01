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
        self.base_url = f"http://{host}"

    async def _request(self, endpoint: str, data: dict = None):
        """Make a request to the Luxor controller."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with async_timeout.timeout(10):
                if data:
                    async with self.session.post(
                        url,
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        response.raise_for_status()
                        return await response.json()
                else:
                    async with self.session.get(url) as response:
                        response.raise_for_status()
                        return await response.json()
        except Exception as err:
            _LOGGER.error("Error connecting to Luxor controller: %s", err)
            raise

    async def get_controller_name(self):
        """Get controller name and type."""
        return await self._request("/ControllerName.json")

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
        response = await self._request("/GroupListGet.json")
        return response.get("GroupList", [])

    async def get_theme_list(self):
        """Get list of themes."""
        response = await self._request("/ThemeListGet.json")
        return response.get("ThemeList", [])

    async def illuminate_group(self, group_number: int, intensity: int):
        """Set group intensity (0-100)."""
        data = {
            "GroupNumber": group_number,
            "Intensity": intensity
        }
        return await self._request("/IlluminateGroup.json", data)

    async def illuminate_theme(self, theme_index: int, on_off: int):
        """Activate a theme."""
        data = {
            "ThemeIndex": theme_index,
            "OnOff": on_off
        }
        return await self._request("/IlluminateTheme.json", data)

    async def set_hue_sat(self, group_number: int, hue: int, sat: int):
        """Set hue and saturation for a color group."""
        data = {
            "GroupNumber": group_number,
            "Hue": hue,
            "Sat": sat
        }
        return await self._request("/SetHueSat.json", data)
