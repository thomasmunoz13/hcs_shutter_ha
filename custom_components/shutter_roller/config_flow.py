import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_NAME, CONF_HOST

@callback
def configured_instances(hass):
    return [entry.data[CONF_HOST] for entry in hass.config_entries.async_entries(DOMAIN)]

class ShutterRollerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_NAME): str,
            vol.Required(CONF_HOST): str,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema)