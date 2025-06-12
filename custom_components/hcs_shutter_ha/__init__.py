import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.const import CONF_NAME, CONF_HOST
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, CONF_COVERS

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Shutter Roller component from YAML configuration."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    covers = conf.get(CONF_COVERS, [])

    for cover in covers:
        name = cover.get(CONF_NAME)
        host = cover.get(CONF_HOST)
        
        hass.data.setdefault(DOMAIN, {}).setdefault(name, {"host": host})
        
        await async_load_platform(hass, "cover", DOMAIN, {"name": name, "host": host}, config)
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Shutter Roller from a config entry."""
    name = entry.data[CONF_NAME]
    host = entry.data[CONF_HOST]
    
    hass.data.setdefault(DOMAIN, {}).setdefault(name, {"host": host})
    
    await hass.config_entries.async_forward_entry_setups(entry, ["cover"])
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unloads(entry, ["cover"])
    
    hass.data[DOMAIN].pop(entry.data[CONF_NAME])
    
    return True