import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "shutter_roller"

async def async_setup(hass: HomeAssistant, config: dict):
    _LOGGER.info("Setting up shutter roller integration")
    return True