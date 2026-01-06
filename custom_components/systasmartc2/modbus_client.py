"""Modbus client for SystaSmartC2."""
import logging
from typing import Any, Dict

from pymodbus.client import ModbusTcpClient

from .const import (
    DHW_STATUS_MAP,
    CIRCULATION_STATUS_MAP,
    HEATING_CIRCUIT_STATUS_MAP,
    SOLAR_STATUS_MAP,
    BOILER_STATUS_MAP,
)

_LOGGER = logging.getLogger(__name__)


class SystaSmartC2ModbusClient:
    """Modbus client for SystaSmartC2."""

    def __init__(self, host: str, port: int, slave_id: int):
        """Initialize the client."""
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.client: ModbusTcpClient | None = None

    def connect(self) -> bool:
        """Connect to the device."""
        try:
            self.client = ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=10,
                retries=3,
            )
            result = self.client.connect()
            _LOGGER.debug(
                "Connection to %s:%s result: %s",
                self.host,
                self.port,
                result,
            )
            return result
        except Exception as e:
            _LOGGER.error(
                "Failed to connect to SystaSmartC2 at %s:%s - %s",
                self.host,
                self.port,
                e,
            )
            return False

    def disconnect(self):
        """Disconnect from the device."""
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None

    def _ensure_connection(self):
        """Ensure we have an active connection."""
        if not self.client or not self.client.is_socket_open():
            if not self.connect():
                raise ConnectionError(
                    f"Cannot connect to SystaSmartC2 at {self.host}:{self.port}"
                )

    def read_bits(self) -> Dict[str, Any]:
        """Read coil/bit registers (Coils 1–8)."""
        data = {}
        try:
            self._ensure_connection()

            result = self.client.read_coils(address=0, count=8, device_id=self.slave_id)

            if not result.isError():
                bits = result.bits[:8]
                data.update({
                    "sh_enabled": bits[0] if len(bits) > 0 else False,
                    "hk1_available": bits[1] if len(bits) > 1 else False,
                    "hk2_available": bits[2] if len(bits) > 2 else False,
                    "dhw_enable": bits[4] if len(bits) > 4 else False,
                    "dhw_disable": bits[5] if len(bits) > 5 else False,
                    "circ_enable": bits[6] if len(bits) > 6 else False,
                    "circ_disable": bits[7] if len(bits) > 7 else False,
                })
                _LOGGER.debug("Read bits successfully: %s", data)
            else:
                _LOGGER.warning("Error reading coils: %s", result)

        except Exception as e:
            _LOGGER.error("Error reading bits: %s", e)

        return data

    def read_input_registers(self) -> Dict[str, Any]:
        """Read input registers (Temperaturen, 30001–30014)."""
        data = {}
        try:
            self._ensure_connection()

            result = self.client.read_input_registers(address=0, count=14, device_id=self.slave_id)

            if not result.isError():
                registers = result.registers
                temp_mapping = [
                    ("temp_outside", 0),
                    ("temp_flow_hk1", 1),
                    ("temp_return_hk1", 2),
                    ("temp_dhw", 3),
                    ("temp_buffer_top", 4),
                    ("temp_buffer_bottom", 5),
                    ("temp_circulation", 6),
                    ("temp_flow_hk2", 7),
                    ("temp_return_hk2", 8),
                    ("temp_room_hk1", 9),
                    ("temp_room_hk2", 10),
                    ("temp_collector", 11),
                    ("temp_boiler_flow", 12),
                    ("temp_boiler_return", 13),
                ]

                for name, idx in temp_mapping:
                    if idx < len(registers):
                        value = registers[idx]
                        if value in [0x8000, 0xFFFF, 0x7FFF]:
                            data[name] = None
                        else:
                            if value > 32767:
                                value -= 65536
                            data[name] = round(value / 10.0, 1)

                _LOGGER.debug("Read input registers successfully: %s", data)
            else:
                _LOGGER.warning("Error reading input registers: %s", result)

        except Exception as e:
            _LOGGER.error("Error reading input registers: %s", e)

        return data

    def read_holding_registers(self) -> Dict[str, Any]:
        """Read holding registers."""
        data = {}
        try:
            self._ensure_connection()

            register_mapping = [
                (2, "setpoint_flow_hk1", True),
                (3, "setpoint_flow_hk2", True),
                (8, "setpoint_dhw", True),
                (34, "status_dhw", False),
                (35, "status_circulation", False),
                (36, "status_hk1", False),
                (37, "status_hk2", False),
                (39, "status_solar", False),
                (41, "status_boiler", False),
                (12, "error_controller", False),
                (13, "error_solar", False),
            ]

            for reg_offset, name, is_temp in register_mapping:
                try:
                    result = self.client.read_holding_registers(address=reg_offset, count=1, device_id=self.slave_id)
                    if not result.isError():
                        value = result.registers[0]
                        if is_temp:
                            if value in [0x8000, 0xFFFF]:
                                data[name] = None
                            else:
                                if value > 32767:
                                    value -= 65536
                                data[name] = round(value / 10.0, 1)
                        else:
                            if value == 0xFFFF and "error" in name:
                                data[name] = None
                            else:
                                data[name] = value
                    else:
                        _LOGGER.debug("Error reading holding register %s: %s", reg_offset, result)
                except Exception as e:
                    _LOGGER.debug("Could not read holding register %s: %s", name, e)

            _LOGGER.debug("Read holding registers successfully: %s", data)

        except Exception as e:
            _LOGGER.error("Error reading holding registers: %s", e)

        return data

    def read_all_data(self) -> Dict[str, Any]:
        """Read all available data from the device."""
        data = {}
        data.update(self.read_bits())
        data.update(self.read_input_registers())
        data.update(self.read_holding_registers())

        status_mappings = [
            ("status_dhw", "status_dhw_text", DHW_STATUS_MAP),
            ("status_circulation", "status_circulation_text", CIRCULATION_STATUS_MAP),
            ("status_hk1", "status_hk1_text", HEATING_CIRCUIT_STATUS_MAP),
            ("status_hk2", "status_hk2_text", HEATING_CIRCUIT_STATUS_MAP),
            ("status_solar", "status_solar_text", SOLAR_STATUS_MAP),
            ("status_boiler", "status_boiler_text", BOILER_STATUS_MAP),
        ]

        for status_key, text_key, mapping in status_mappings:
            if status_key in data and data[status_key] is not None:
                data[text_key] = mapping.get(data[status_key], f"Unbekannt ({data[status_key]})")

        _LOGGER.debug("Final combined data: %s", data)
        return data

    def write_holding_register(self, register: int, value: int) -> bool:
        """Write a holding register."""
        try:
            self._ensure_connection()
            result = self.client.write_register(address=register, value=value, device_id=self.slave_id)
            success = not result.isError()
            _LOGGER.debug("Write register %s = %s: %s", register, value, success)
            return success
        except Exception as e:
            _LOGGER.error("Error writing register %s: %s", register, e)
            return False

    def write_coil(self, coil: int, value: bool) -> bool:
        """Write a coil."""
        try:
            self._ensure_connection()
            result = self.client.write_coil(address=coil, value=value, device_id=self.slave_id)
            success = not result.isError()
            _LOGGER.debug("Write coil %s = %s: %s", coil, value, success)
            return success
        except Exception as e:
            _LOGGER.error("Error writing coil %s: %s", coil, e)
            return False