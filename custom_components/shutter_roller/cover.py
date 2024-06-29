import requests
import logging
from homeassistant.components.cover import CoverEntity
from homeassistant.const import CONF_NAME, CONF_HOST

_LOGGER = logging.getLogger(__name__)

DOMAIN = "shutter_roller"

def setup_platform(hass, config, add_entities, discovery_info=None):
    covers = config.get(DOMAIN, [])
    devices = []

    for cover in covers:
        name = cover[CONF_NAME]
        host = cover[CONF_HOST]
        devices.append(ShutterRollerCover(name, host))

    add_entities(devices)

class ShutterRollerAPI:
    def __init__(self, base_url, shutter_name, logger):
        self.base_url = f"{base_url}/shutter/{shutter_name}"
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
    def __init__(self, name, host):
        self._name = name
        self._host = host
        self._position = 0
        self._is_closed = True
        self.api = ShutterRollerAPI(host, name, _LOGGER)

    @property
    def name(self):
        return self._name

    @property
    def is_closed(self):
        return self._is_closed

    @property
    def current_cover_position(self):
        return self._position

    def close_cover(self, **kwargs):
        if self.api.set_position(0):
            self._is_closed = True
            self._position = 0
            self.schedule_update_ha_state()

    def open_cover(self, **kwargs):
        if self.api.set_position(100):
            self._is_closed = False
            self._position = 100
            self.schedule_update_ha_state()

    def set_cover_position(self, **kwargs):
        position = kwargs.get('position', 0)
        if self.api.set_position(position):
            self._position = position
            self._is_closed = position == 0
            self.schedule_update_ha_state()

    def update(self):
        position = self.api.get_position()
        if position != -1:
            self._position = position
            self._is_closed = position == 0
            self.schedule_update_ha_state()