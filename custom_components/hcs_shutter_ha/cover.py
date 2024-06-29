import requests
import logging
from homeassistant.components.cover import CoverEntity
from homeassistant.const import CONF_NAME, CONF_HOST
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from .const import DOMAIN, MANUFACTURER, MODEL, SW_VERSION

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass: HomeAssistant, config: dict, async_add_entities: AddEntitiesCallback, discovery_info=None):
    """Set up the Shutter Roller platform from YAML configuration."""
    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    host = discovery_info[CONF_HOST]
    shutter_id = discovery_info['shutter_id']
    _LOGGER.debug(f"Setting up Shutter Roller cover: {name} with host: {host}")
    
    async_add_entities([ShutterRollerCover(hass, name, host, shutter_id)])

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Shutter Roller cover from a config entry."""
    name = entry.data['name']
    host = entry.data[CONF_HOST]
    shutter_id = entry.data['shutter_id']
    
    async_add_entities([ShutterRollerCover(hass, name, host, shutter_id)])

class ShutterRollerAPI:
    def __init__(self, base_url, shutter_id, logger):
        self.base_url = f"{base_url}/shutter/{shutter_id}"
        self.logger = logger

    def get_position(self):
        try:
            response = requests.get(self.base_url, timeout=60)
            response.raise_for_status()
            self.logger.info(response.json())
            return response.json()['data']['currentOpenRatio'] * 100
        except requests.exceptions.RequestException as error:
            self.logger.error(f"Error getting position: {error}")
            return -1

    def set_position(self, value):
        try:
            response = requests.get(f"{self.base_url}/ratio?arg={value / 100.0}", timeout=60)
            response.raise_for_status()
            self.logger.info(response)
            return True
        except requests.exceptions.RequestException as error:
            self.logger.error(f"Error setting position: {error}")
            return False

class ShutterRollerCover(CoverEntity):
    def __init__(self, hass: HomeAssistant, name, host, shutter_id):
        self.hass = hass
        self._name = name
        self._host = host
        self._shutter_id = shutter_id
        self._position = 0
        self._is_closed = True
        self.api = ShutterRollerAPI(host, shutter_id, _LOGGER)

    @property
    def name(self):
        return self._name

    @property
    def is_closed(self):
        return self._is_closed

    @property
    def current_cover_position(self):
        return self._position

    @property
    def unique_id(self):
        return f"{self._host}_{self._shutter_id}"

    async def async_close_cover(self, **kwargs):
        result = await self.hass.async_add_executor_job(self.api.set_position, 0)
        if result:
            self._is_closed = True
            self._position = 0
            self.async_schedule_update_ha_state()

    async def async_open_cover(self, **kwargs):
        result = await self.hass.async_add_executor_job(self.api.set_position, 100)
        if result:
            self._is_closed = False
            self._position = 100
            self.async_schedule_update_ha_state()

    async def async_set_cover_position(self, **kwargs):
        position = kwargs.get('position', 0)
        result = await self.hass.async_add_executor_job(self.api.set_position, position)
        if result:
            self._position = position
            self._is_closed = position == 0
            self.async_schedule_update_ha_state()

    async def async_update(self):
        position = await self.hass.async_add_executor_job(self.api.get_position)
        if position != -1:
            self._position = position
            self._is_closed = position == 0
            self.async_schedule_update_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this cover."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._shutter_id)},
            name=self._name,
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=SW_VERSION,
            entry_type=DeviceEntryType.SERVICE
        )