"""Sensor platform for SystaSmartC2 with dynamic feature loading."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MANUFACTURER,
    MODEL,
    CONF_ENABLE_SOLAR_SENSORS,
    CONF_ENABLE_ENERGY_SENSORS,
    CONF_ENABLE_BOILER_SENSORS,
    CONF_ENABLE_PELLET_SENSORS,
    CONF_ENABLE_WOOD_BOILER_SENSORS,
    CONF_ENABLE_POOL_SENSORS,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    config = hass.data[DOMAIN][config_entry.entry_id]["config"]
    data = coordinator.data

    entities = []

    def add_if_valid(key, name, unit=None, device_class=None, state_class=None):
        value = data.get(key)
        if value is not None:
            if device_class == SensorDeviceClass.TEMPERATURE and (value < -50 or value > 100):
                return
            if device_class in (SensorDeviceClass.ENERGY, SensorDeviceClass.POWER) and value < 0:
                return
            entities.append(
                SystaSmartC2Sensor(coordinator, key, name, unit, device_class, state_class)
            )

    # Basis-Sensoren (immer)
    base_sensors = [
        ("temp_outside", "Außentemperatur", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        ("temp_buffer_top", "Puffer oben", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        ("temp_buffer_bottom", "Puffer unten", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        ("temp_dhw", "Warmwasser", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        ("temp_circulation", "Zirkulation", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        ("setpoint_dhw", "Soll Warmwasser", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    ]
    for key, name, unit, device_class in base_sensors:
        add_if_valid(key, name, unit, device_class)

    if data.get("hk1_available", False):
        add_if_valid("temp_flow_hk1", "Vorlauf HK1", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("temp_return_hk1", "Rücklauf HK1", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("temp_room_hk1", "Raum HK1", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("setpoint_flow_hk1", "Soll Vorlauf HK1", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)

    if data.get("hk2_available", False):
        add_if_valid("temp_flow_hk2", "Vorlauf HK2", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("temp_return_hk2", "Rücklauf HK2", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("temp_room_hk2", "Raum HK2", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("setpoint_flow_hk2", "Soll Vorlauf HK2", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)

    if config.get(CONF_ENABLE_SOLAR_SENSORS, False):
        add_if_valid("temp_collector", "Kollektor", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("solar_power", "Solarleistung aktuell", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER)

        if config.get(CONF_ENABLE_ENERGY_SENSORS, False):
            add_if_valid("solar_energy_today", "Solarertrag heute", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING)
            add_if_valid("solar_energy_total", "Solarertrag gesamt", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL)

    if config.get(CONF_ENABLE_BOILER_SENSORS, False):
        add_if_valid("temp_boiler_flow", "Kesselvorlauf", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("temp_boiler_return", "Kesselrücklauf", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("setpoint_boiler", "Kesselsoll", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)

        if config.get(CONF_ENABLE_ENERGY_SENSORS, False):
            add_if_valid("boiler_hours", "Betriebsstunden Kessel", UnitOfTime.HOURS, SensorDeviceClass.DURATION, SensorStateClass.TOTAL)
            add_if_valid("boiler_starts", "Anzahl Starts Kessel", None, None, SensorStateClass.TOTAL_INCREASING)

    if config.get(CONF_ENABLE_PELLET_SENSORS, False):
        add_if_valid("pellet_hours", "Betriebsstunden Pellet", UnitOfTime.HOURS, SensorDeviceClass.DURATION)
        add_if_valid("pellet_consumption", "Pelletverbrauch gesamt", "t", None)

    if config.get(CONF_ENABLE_WOOD_BOILER_SENSORS, False):
        add_if_valid("temp_wood_boiler_flow", "Vorlauf Holzkessel", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("temp_wood_boiler_return", "Rücklauf Holzkessel", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("temp_wood_buffer_top", "Holzpuffer oben", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)

    if config.get(CONF_ENABLE_POOL_SENSORS, False):
        add_if_valid("temp_pool", "Schwimmbad", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("temp_pool_flow", "Vorlauf Pool", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
        add_if_valid("temp_pool_return", "Rücklauf Pool", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)

    # Status-Texte (immer)
    status_texts = [
        ("status_dhw_text", "Status Warmwasser"),
        ("status_circulation_text", "Status Zirkulation"),
        ("status_hk1_text", "Status HK1"),
        ("status_hk2_text", "Status HK2"),
        ("status_solar_text", "Status Solar"),
        ("status_boiler_text", "Status Kessel"),
    ]
    for key, name in status_texts:
        entities.append(SystaSmartC2Sensor(coordinator, key, name))

    add_if_valid("error_controller", "Störcode Regler")
    add_if_valid("smarthome_error", "Störcode Smarthome")

    if config.get(CONF_ENABLE_ENERGY_SENSORS, False):
        add_if_valid("energy_dhw", "Wärmemenge Warmwasser", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL)
        add_if_valid("energy_circulation", "Wärmemenge Zirkulation", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL)

    async_add_entities(entities)


class SystaSmartC2Sensor(CoordinatorEntity, SensorEntity):
    """Representation of a SystaSmartC2 sensor."""

    def __init__(self, coordinator, key, name, unit=None, device_class=None, state_class=None):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def unique_id(self):
        return f"systasmartc2_{self._key}"

    @property
    def native_value(self):
        value = self.coordinator.data.get(self._key)
        if value is None and "_text" in self._key:
            return "Unbekannt"
        return value

    @property
    def icon(self):
        """Return a suitable icon for the sensor."""
        icons = {
            "temp_outside": "mdi:thermometer",
            "temp_flow_hk1": "mdi:thermometer-chevron-up",
            "temp_return_hk1": "mdi:thermometer-chevron-down",
            "temp_flow_hk2": "mdi:thermometer-chevron-up",
            "temp_return_hk2": "mdi:thermometer-chevron-down",
            "temp_room_hk1": "mdi:home-thermometer",
            "temp_room_hk2": "mdi:home-thermometer",
            "temp_dhw": "mdi:water-thermometer",
            "temp_buffer_top": "mdi:radiator",
            "temp_buffer_bottom": "mdi:radiator-disabled",
            "temp_circulation": "mdi:pipe",
            "temp_collector": "mdi:solar-power",
            "temp_boiler_flow": "mdi:fire",
            "temp_boiler_return": "mdi:fire",
            "temp_wood_boiler_flow": "mdi:fire",
            "temp_wood_boiler_return": "mdi:fire",
            "temp_wood_buffer_top": "mdi:radiator",
            "temp_pool": "mdi:pool",
            "temp_pool_flow": "mdi:pool-thermometer",
            "temp_pool_return": "mdi:pool-thermometer",
            "setpoint_flow_hk1": "mdi:thermometer-chevron-up",
            "setpoint_flow_hk2": "mdi:thermometer-chevron-up",
            "setpoint_dhw": "mdi:water-thermometer-outline",
            "setpoint_boiler": "mdi:thermometer-chevron-up",
            "status_dhw_text": "mdi:water-pump",
            "status_circulation_text": "mdi:pipe-leak",
            "status_hk1_text": "mdi:radiator",
            "status_hk2_text": "mdi:radiator",
            "status_solar_text": "mdi:solar-power",
            "status_boiler_text": "mdi:fire",
            "error_controller": "mdi:alert-circle",
            "smarthome_error": "mdi:alert-circle-outline",
            "energy_dhw": "mdi:flash",
            "energy_circulation": "mdi:flash-outline",
            "solar_energy_today": "mdi:weather-sunny",
            "solar_energy_total": "mdi:weather-sunny",
            "solar_power": "mdi:solar-power",
            "boiler_hours": "mdi:clock-outline",
            "boiler_starts": "mdi:counter",
            "pellet_hours": "mdi:clock-outline",
            "pellet_consumption": "mdi:sack",
        }
        return icons.get(self._key, "mdi:thermometer-lines")

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