"""Services for SystaSmartC2."""
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_SET_HEATING_TEMPERATURE = "set_heating_temperature"
SERVICE_SET_DHW_TEMPERATURE = "set_dhw_temperature"
SERVICE_CONTROL_DHW = "control_dhw"

SET_HEATING_TEMPERATURE_SCHEMA = vol.Schema({
    vol.Required("circuit"): cv.string,
    vol.Required("temperature"): vol.Coerce(float),
})

SET_DHW_TEMPERATURE_SCHEMA = vol.Schema({
    vol.Required("temperature"): vol.Coerce(float),
})

CONTROL_DHW_SCHEMA = vol.Schema({
    vol.Required("enable"): cv.boolean,
})

async def async_setup_services(hass: HomeAssistant):
    """Set up services for SystaSmartC2."""
    
    async def set_heating_temperature(call: ServiceCall):
        circuit = call.data["circuit"]
        temperature = call.data["temperature"]
        
        if circuit not in ["1", "2"]:
            _LOGGER.error("Invalid circuit: %s. Must be '1' or '2'", circuit)
            return
        
        if not 5.0 <= temperature <= 80.0:
            _LOGGER.error("Temperature %s out of range (5-80°C)", temperature)
            return
        
        success_count = 0
        for entry_id, data in hass.data[DOMAIN].items():
            modbus_client = data["modbus_client"]
            coordinator = data["coordinator"]
            
            register = 2 if circuit == "1" else 3
            reg_value = int(temperature * 10)
            
            success = await hass.async_add_executor_job(
                modbus_client.write_holding_register, register, reg_value
            )
            
            if success:
                await coordinator.async_request_refresh()
                success_count += 1
                _LOGGER.info("Set heating circuit %s temperature to %.1f°C", circuit, temperature)
            else:
                _LOGGER.error("Failed to set heating circuit %s temperature", circuit)
        
        if success_count == 0:
            _LOGGER.warning("No SystaSmartC2 devices found or all writes failed")
    
    async def set_dhw_temperature(call: ServiceCall):
        temperature = call.data["temperature"]
        
        if not 10.0 <= temperature <= 70.0:
            _LOGGER.error("Temperature %s out of range (10-70°C)", temperature)
            return
        
        success_count = 0
        for entry_id, data in hass.data[DOMAIN].items():
            modbus_client = data["modbus_client"]
            coordinator = data["coordinator"]
            
            reg_value = int(temperature * 10)
            
            success = await hass.async_add_executor_job(
                modbus_client.write_holding_register, 8, reg_value
            )
            
            if success:
                await coordinator.async_request_refresh()
                success_count += 1
                _LOGGER.info("Set DHW temperature to %.1f°C", temperature)
            else:
                _LOGGER.error("Failed to set DHW temperature")
        
        if success_count == 0:
            _LOGGER.warning("No SystaSmartC2 devices found or all writes failed")
    
    async def control_dhw(call: ServiceCall):
        enable = call.data["enable"]
        
        success_count = 0
        for entry_id, data in hass.data[DOMAIN].items():
            modbus_client = data["modbus_client"]
            coordinator = data["coordinator"]
            
            if enable:
                await hass.async_add_executor_job(
                    modbus_client.write_coil, 4, True
                )
                await hass.async_add_executor_job(
                    modbus_client.write_coil, 5, False
                )
                _LOGGER.info("DHW enabled")
            else:
                await hass.async_add_executor_job(
                    modbus_client.write_coil, 5, True
                )
                await hass.async_add_executor_job(
                    modbus_client.write_coil, 4, False
                )
                _LOGGER.info("DHW disabled")
            
            await coordinator.async_request_refresh()
            success_count += 1
        
        if success_count == 0:
            _LOGGER.warning("No SystaSmartC2 devices found")
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_HEATING_TEMPERATURE,
        set_heating_temperature,
        schema=SET_HEATING_TEMPERATURE_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_DHW_TEMPERATURE,
        set_dhw_temperature,
        schema=SET_DHW_TEMPERATURE_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_CONTROL_DHW,
        control_dhw,
        schema=CONTROL_DHW_SCHEMA,
    )