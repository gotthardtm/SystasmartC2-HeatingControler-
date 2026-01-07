"""Climate platform for SystaSmartC2."""
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the SystaSmartC2 climate entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    modbus_client = hass.data[DOMAIN][config_entry.entry_id]["modbus_client"]
    data = coordinator.data

    entities = []

    if data.get("hk1_available", False):
        entities.append(SystaSmartC2Climate(coordinator, modbus_client, "hk1", "Heizkreis 1"))

    if data.get("hk2_available", False):
        entities.append(SystaSmartC2Climate(coordinator, modbus_client, "hk2", "Heizkreis 2"))

    async_add_entities(entities)


class SystaSmartC2Climate(CoordinatorEntity, ClimateEntity):
    """Representation of a SystaSmartC2 heating circuit."""

    def __init__(self, coordinator, modbus_client, circuit_id, name):
        super().__init__(coordinator)
        self._modbus_client = modbus_client
        self._circuit_id = circuit_id
        self._attr_name = name
        self._circuit_num = circuit_id[-1]
        self._attr_icon = "mdi:radiator"
        
    @property
    def unique_id(self):
        return f"systasmartc2_climate_{self._circuit_id}"
    
    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS
    
    @property
    def current_temperature(self):
        return self.coordinator.data.get(f"temp_room_{self._circuit_id}")
    
    @property
    def target_temperature(self):
        return self.coordinator.data.get(f"setpoint_flow_{self._circuit_id}")
    
    @property
    def hvac_mode(self):
        status = self.coordinator.data.get(f"status_{self._circuit_id}")
        if status == 0:
            return HVACMode.OFF
        elif status == 1:
            return HVACMode.HEAT
        elif status == 6:
            return HVACMode.HEAT
        else:
            return HVACMode.AUTO
    
    @property
    def hvac_modes(self):
        return [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    
    @property
    def hvac_action(self):
        from homeassistant.components.climate import HVACAction
        status = self.coordinator.data.get(f"status_{self._circuit_id}")
        if status == 1:
            return HVACAction.HEATING
        elif status == 0:
            return HVACAction.OFF
        else:
            return HVACAction.IDLE
    
    @property
    def supported_features(self):
        return ClimateEntityFeature.TARGET_TEMPERATURE
    
    @property
    def min_temp(self):
        return 5.0
    
    @property
    def max_temp(self):
        max_temp = self.coordinator.data.get(f"max_flow_temp_{self._circuit_id}")
        return max_temp if max_temp else 80.0
    
    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        
        if not 5.0 <= temperature <= 80.0:
            _LOGGER.warning("Temperature %s out of range (5-80°C)", temperature)
            return
        
        reg_value = int(temperature * 10)
        register = 2 if self._circuit_num == "1" else 3
        
        success = await self.hass.async_add_executor_job(
            self._modbus_client.write_holding_register, register, reg_value
        )
        
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set temperature for %s", self._circuit_id)
    
    @property
    def available(self):
        return self.coordinator.data.get(f"temp_flow_{self._circuit_id}") is not None
    
    @property
    def extra_state_attributes(self):
        attrs = {}
        flow_temp = self.coordinator.data.get(f"temp_flow_{self._circuit_id}")
        if flow_temp is not None:
            attrs["flow_temperature"] = flow_temp
        
        return_temp = self.coordinator.data.get(f"temp_return_{self._circuit_id}")
        if return_temp is not None:
            attrs["return_temperature"] = return_temp
        
        status_text = self.coordinator.data.get(f"status_{self._circuit_id}_text")
        if status_text:
            attrs["status"] = status_text
        
        return attrs
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "systasmartc2")},
            "name": "SystaSmartC2",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }