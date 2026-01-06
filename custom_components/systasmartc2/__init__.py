"""SystaSmartC2 Integration with dynamic component loading."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import entity_registry as er

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_SLAVE_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    CONF_ENABLE_WATER_HEATER,
    CONF_ENABLE_SERVICES,
)
from .modbus_client import SystaSmartC2ModbusClient

_LOGGER = logging.getLogger(__name__)

BASE_PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SystaSmartC2 from a config entry with dynamic platform loading."""
    _LOGGER.debug("Setting up SystaSmartC2 entry %s", entry.entry_id)

    config = {**entry.data, **entry.options}

    host = config[CONF_HOST]
    port = config[CONF_PORT]
    slave_id = config[CONF_SLAVE_ID]
    scan_interval = config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    modbus_client = SystaSmartC2ModbusClient(host, port, slave_id)

    if not await hass.async_add_executor_job(modbus_client.connect):
        _LOGGER.error("Failed to connect to SystaSmartC2 at %s:%s", host, port)
        return False

    async def async_update_data():
        try:
            await hass.async_add_executor_job(modbus_client._ensure_connection)
            data = await hass.async_add_executor_job(modbus_client.read_all_data)
            return data
        except Exception as err:
            _LOGGER.error("Error communicating with SystaSmartC2: %s", err)
            raise UpdateFailed(f"Error communicating with SystaSmartC2: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{entry.entry_id}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "modbus_client": modbus_client,
        "config": config,
    }

    platforms = BASE_PLATFORMS.copy()

    if config.get(CONF_ENABLE_WATER_HEATER, True):
        platforms.append(Platform.WATER_HEATER)
        _LOGGER.info("Water Heater platform enabled for entry %s", entry.entry_id)

    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    if config.get(CONF_ENABLE_SERVICES, True):
        current_entries = hass.config_entries.async_entries(DOMAIN)
        if len(current_entries) == 1 or entry is current_entries[0]:
            try:
                from . import services
                await services.async_setup_services(hass)
                _LOGGER.info("SystaSmartC2 services registered")
            except ImportError as err:
                _LOGGER.warning("Could not load services module: %s", err)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading SystaSmartC2 entry %s", entry.entry_id)

    config = {**entry.data, **entry.options}

    platforms = BASE_PLATFORMS.copy()
    if config.get(CONF_ENABLE_WATER_HEATER, True):
        platforms.append(Platform.WATER_HEATER)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, platforms)

    if unload_ok:
        client_data = hass.data[DOMAIN].get(entry.entry_id)
        if client_data and client_data.get("modbus_client"):
            await hass.async_add_executor_job(client_data["modbus_client"].disconnect)

        # Alte Entities bereinigen
        entity_registry = er.async_get(hass)
        entities_to_remove = [
            ent_id for ent_id in entity_registry.entities
            if entity_registry.entities[ent_id].domain in ["sensor", "binary_sensor", "climate", "water_heater"]
            and entity_registry.entities[ent_id].config_entry_id == entry.entry_id
        ]
        for ent_id in entities_to_remove:
            entity_registry.async_remove(ent_id)
        _LOGGER.debug("Removed %s old entities", len(entities_to_remove))

        hass.data[DOMAIN].pop(entry.entry_id, None)

 # Services haben keine unload-Funktion nötig – HA entfernt sie automatisch
        if not hass.data[DOMAIN] and config.get(CONF_ENABLE_SERVICES, True):
            _LOGGER.debug("SystaSmartC2 services automatically unregistered by Home Assistant")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)