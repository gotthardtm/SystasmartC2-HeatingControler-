"""Config flow for SystaSmartC2 with component selection."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_NAME,
    CONF_SLAVE_ID,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    CONF_ENABLE_WATER_HEATER,
    CONF_ENABLE_SERVICES,
    CONF_ENABLE_SOLAR_SENSORS,
    CONF_ENABLE_ENERGY_SENSORS,
    CONF_ENABLE_BOILER_SENSORS,
    CONF_ENABLE_PELLET_SENSORS,
    CONF_ENABLE_WOOD_BOILER_SENSORS,
    CONF_ENABLE_POOL_SENSORS,
)

_LOGGER = logging.getLogger(__name__)

CONNECTION_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME, default="SystaSmartC2"): str,
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
    vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
})


async def validate_input(hass: HomeAssistant, data: dict) -> Dict[str, Any]:
    from .modbus_client import SystaSmartC2ModbusClient
    
    client = SystaSmartC2ModbusClient(data[CONF_HOST], data[CONF_PORT], data[CONF_SLAVE_ID])
    
    if not await hass.async_add_executor_job(client.connect):
        raise CannotConnect
    
    try:
        all_data = await hass.async_add_executor_job(client.read_all_data)
        
        detected = {
            "hk1_available": all_data.get("hk1_available", False),
            "hk2_available": all_data.get("hk2_available", False),
            "dhw_available": all_data.get("temp_dhw") is not None,
            "solar_available": all_data.get("temp_collector") is not None and all_data.get("temp_collector") > -50,
            "boiler_available": all_data.get("temp_boiler_flow") is not None,
            "pellet_available": all_data.get("status_pellet") is not None and all_data.get("status_pellet") != 0xFFFF,
            "wood_boiler_available": all_data.get("temp_wood_boiler_flow") is not None,
            "pool_available": all_data.get("temp_pool") is not None,
        }
        
        _LOGGER.info("Detected components: %s", detected)
        
    except Exception as ex:
        _LOGGER.error("Error validating connection: %s", ex)
        raise InvalidData
    finally:
        client.disconnect()
    
    return {
        "title": data[CONF_NAME],
        "detected": detected
    }


class SystaSmartC2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SystaSmartC2."""

    VERSION = 1

    def __init__(self):
        self._connection_data = {}
        self._detected_components = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        errors = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                await self.async_set_unique_id(f"{user_input[CONF_HOST]}_{user_input[CONF_PORT]}")
                self._abort_if_unique_id_configured()
                
                self._connection_data = user_input
                self._detected_components = info.get("detected", {})
                
                return await self.async_step_components()
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidData:
                errors["base"] = "invalid_data"
            except Exception:
                _LOGGER.exception("Unexpected exception during setup")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", 
            data_schema=CONNECTION_SCHEMA, 
            errors=errors,
        )

    async def async_step_components(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        if user_input is not None:
            config_data = {**self._connection_data, **user_input}
            return self.async_create_entry(title=self._connection_data[CONF_NAME], data=config_data)

        schema_dict = {
            vol.Optional(CONF_ENABLE_SERVICES, default=True): bool,
        }

        if self._detected_components.get("dhw_available", False):
            schema_dict[vol.Optional(CONF_ENABLE_WATER_HEATER, default=True)] = bool

        if self._detected_components.get("solar_available", False):
            schema_dict[vol.Optional(CONF_ENABLE_SOLAR_SENSORS, default=True)] = bool
            schema_dict[vol.Optional(CONF_ENABLE_ENERGY_SENSORS, default=True)] = bool

        if self._detected_components.get("boiler_available", False):
            schema_dict[vol.Optional(CONF_ENABLE_BOILER_SENSORS, default=True)] = bool

        if self._detected_components.get("pellet_available", False):
            schema_dict[vol.Optional(CONF_ENABLE_PELLET_SENSORS, default=True)] = bool


            schema_dict[vol.Optional(CONF_ENABLE_WOOD_BOILER_SENSORS, default=False)] = bool

        if self._detected_components.get("pool_available", False):
            schema_dict[vol.Optional(CONF_ENABLE_POOL_SENSORS, default=True)] = bool

        components_schema = vol.Schema(schema_dict)
        
        return self.async_show_form(
            step_id="components",
            data_schema=components_schema,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SystaSmartC2OptionsFlow(config_entry)


class SystaSmartC2OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                options={**self._config_entry.options, **user_input}
            )
            await self.hass.config_entries.async_reload(self._config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        def get_value(key, default):
            return self._config_entry.options.get(
                key,
                self._config_entry.data.get(key, default)
            )

        options_dict = {
            vol.Optional(CONF_SCAN_INTERVAL, default=get_value(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): int,
            vol.Optional(CONF_ENABLE_WATER_HEATER, default=get_value(CONF_ENABLE_WATER_HEATER, True)): bool,
            vol.Optional(CONF_ENABLE_SERVICES, default=get_value(CONF_ENABLE_SERVICES, True)): bool,
            vol.Optional(CONF_ENABLE_SOLAR_SENSORS, default=get_value(CONF_ENABLE_SOLAR_SENSORS, True)): bool,
            vol.Optional(CONF_ENABLE_ENERGY_SENSORS, default=get_value(CONF_ENABLE_ENERGY_SENSORS, False)): bool,
            vol.Optional(CONF_ENABLE_BOILER_SENSORS, default=get_value(CONF_ENABLE_BOILER_SENSORS, True)): bool,
            vol.Optional(CONF_ENABLE_PELLET_SENSORS, default=get_value(CONF_ENABLE_PELLET_SENSORS, False)): bool,
            vol.Optional(CONF_ENABLE_WOOD_BOILER_SENSORS, default=get_value(CONF_ENABLE_WOOD_BOILER_SENSORS, False)): bool,
            vol.Optional(CONF_ENABLE_POOL_SENSORS, default=get_value(CONF_ENABLE_POOL_SENSORS, False)): bool,
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(options_dict),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidData(HomeAssistantError):
    """Error to indicate there is invalid data."""