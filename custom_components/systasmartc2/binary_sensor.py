"""Binary sensor platform for SystaSmartC2."""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the SystaSmartC2 binary sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    entities = []
    
    binary_sensors = [
        ("sh_enabled", "Smarthome aktiv", BinarySensorDeviceClass.CONNECTIVITY, "mdi:home-assistant"),
        ("hk1_available", "Heizkreis 1 vorhanden", None, "mdi:radiator"),
        ("hk2_available", "Heizkreis 2 vorhanden", None, "mdi:radiator"),
        ("dhw_enable", "Warmwasser freigegeben", None, "mdi:water-pump"),
        ("dhw_disable", "Warmwasser gesperrt", BinarySensorDeviceClass.PROBLEM, "mdi:water-pump-off"),
        ("circ_enable", "Zirkulation freigegeben", None, "mdi:pipe"),
        ("circ_disable", "Zirkulation gesperrt", BinarySensorDeviceClass.PROBLEM, "mdi:pipe-disconnected"),
    ]
    
    for key, name, device_class, icon in binary_sensors:
        entities.append(SystaSmartC2BinarySensor(coordinator, key, name, device_class, icon))
    
    async_add_entities(entities)


class SystaSmartC2BinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a SystaSmartC2 binary sensor."""

    def __init__(self, coordinator, key, name, device_class=None, icon=None):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_device_class = device_class
        self._attr_icon = icon
        
    @property
    def unique_id(self):
        return f"systasmartc2_{self._key}"
    
    @property
    def is_on(self):
        return self.coordinator.data.get(self._key, False)
    
    @property
    def available(self):
        return self.coordinator.last_update_success
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "systasmartc2")},
            "name": "SystaSmartC2",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }