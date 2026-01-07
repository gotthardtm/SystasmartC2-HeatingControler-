"""Water heater platform for SystaSmartC2."""
import logging

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
    STATE_OFF,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, CONF_ENABLE_WATER_HEATER

_LOGGER = logging.getLogger(__name__)

STATE_HEATING = "heating"
STATE_IDLE = "idle"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the SystaSmartC2 water heater."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    modbus_client = hass.data[DOMAIN][config_entry.entry_id]["modbus_client"]
    config = hass.data[DOMAIN][config_entry.entry_id]["config"]
    data = coordinator.data

    if config.get(CONF_ENABLE_WATER_HEATER, True) and data.get("temp_dhw") is not None:
        async_add_entities([SystaSmartC2WaterHeater(coordinator, modbus_client)])

class SystaSmartC2WaterHeater(CoordinatorEntity, WaterHeaterEntity):
    """Representation of a SystaSmartC2 water heater."""

    def __init__(self, coordinator, modbus_client):
        super().__init__(coordinator)
        self._modbus_client = modbus_client
        self._attr_operation_list = [STATE_OFF, STATE_HEATING, STATE_IDLE]
        self._attr_icon = "mdi:water-boiler"

    @property
    def unique_id(self):
        return "systasmartc2_water_heater"

    @property
    def name(self):
        return "Warmwasser"

    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self):
        return self.coordinator.data.get("temp_dhw")

    @property
    def target_temperature(self):
        return self.coordinator.data.get("setpoint_dhw")

    @property
    def min_temp(self):
        return 10.0

    @property
    def max_temp(self):
        return 70.0

    @property
    def supported_features(self):
        return (
            WaterHeaterEntityFeature.TARGET_TEMPERATURE |
            WaterHeaterEntityFeature.ON_OFF
        )

    @property
    def current_operation(self):
        status = self.coordinator.data.get("status_dhw")
        if status == 1:
            return STATE_HEATING
        elif status in [3, 13]:
            return STATE_OFF
        else:
            return STATE_IDLE

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        if not 10.0 <= temperature <= 70.0:
            _LOGGER.warning("Temperature %s out of range (10-70°C)", temperature)
            return

        reg_value = int(temperature * 10)

        success = await self.hass.async_add_executor_job(
            self._modbus_client.write_holding_register, 8, reg_value
        )

        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set DHW temperature")

    async def async_turn_on(self):
        await self.hass.async_add_executor_job(
            self._modbus_client.write_coil, 4, True
        )
        await self.hass.async_add_executor_job(
            self._modbus_client.write_coil, 5, False
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        await self.hass.async_add_executor_job(
            self._modbus_client.write_coil, 5, True
        )
        await self.hass.async_add_executor_job(
            self._modbus_client.write_coil, 4, False
        )
        await self.coordinator.async_request_refresh()

    @property
    def available(self):
        return self.coordinator.data.get("temp_dhw") is not None

    @property
    def extra_state_attributes(self):
        attrs = {}
        status_text = self.coordinator.data.get("status_dhw_text")
        if status_text:
            attrs["status"] = status_text

        circ_text = self.coordinator.data.get("status_circulation_text")
        if circ_text:
            attrs["circulation_status"] = circ_text

        circ_temp = self.coordinator.data.get("temp_circulation")
        if circ_temp is not None:
            attrs["circulation_temperature"] = circ_temp

        return attrs

    @property
    def icon(self):
        """Return icon for water heater."""
        return "mdi:water-boiler"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "systasmartc2")},
            "name": "SystaSmartC2",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }