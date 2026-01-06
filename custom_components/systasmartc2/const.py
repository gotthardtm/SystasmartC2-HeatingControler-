"""Constants for the SystaSmartC2 integration."""

DOMAIN = "systasmartc2"
MANUFACTURER = "Paradigma"
MODEL = "SystaSmartC2"

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_NAME = "name"

# Feature flags - Component activation
CONF_ENABLE_WATER_HEATER = "enable_water_heater"
CONF_ENABLE_SERVICES = "enable_services"
CONF_ENABLE_SOLAR_SENSORS = "enable_solar_sensors"
CONF_ENABLE_ENERGY_SENSORS = "enable_energy_sensors"
CONF_ENABLE_BOILER_SENSORS = "enable_boiler_sensors"
CONF_ENABLE_PELLET_SENSORS = "enable_pellet_sensors"  # Pelletskessel/Pelletsofen
CONF_ENABLE_WOOD_BOILER_SENSORS = "enable_wood_boiler_sensors"  # Holz-/Scheitholzkessel
CONF_ENABLE_POOL_SENSORS = "enable_pool_sensors"

# Default values
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL = 30

# Modbus register definitions for all components
MODBUS_INPUT_REGISTERS = {
    # Basis-Temperatursensoren (immer verfügbar)
    30001: {"name": "temp_outside", "description": "Außentemperatur", "unit": "°C", "scale": 0.1},
    30002: {"name": "temp_flow_hk1", "description": "Vorlauftemperatur HK1", "unit": "°C", "scale": 0.1},
    30003: {"name": "temp_return_hk1", "description": "Rücklauftemperatur HK1", "unit": "°C", "scale": 0.1},
    30004: {"name": "temp_dhw", "description": "Warmwassertemperatur", "unit": "°C", "scale": 0.1},
    30005: {"name": "temp_buffer_top", "description": "Puffertemperatur oben", "unit": "°C", "scale": 0.1},
    30006: {"name": "temp_buffer_bottom", "description": "Puffertemperatur unten", "unit": "°C", "scale": 0.1},
    30007: {"name": "temp_circulation", "description": "Rücklauftemperatur Zirkulation", "unit": "°C", "scale": 0.1},
    30008: {"name": "temp_flow_hk2", "description": "Vorlauftemperatur HK2", "unit": "°C", "scale": 0.1},
    30009: {"name": "temp_return_hk2", "description": "Rücklauftemperatur HK2", "unit": "°C", "scale": 0.1},
    30010: {"name": "temp_room_hk1", "description": "Raumtemperatur HK1", "unit": "°C", "scale": 0.1},
    30011: {"name": "temp_room_hk2", "description": "Raumtemperatur HK2", "unit": "°C", "scale": 0.1},
    
    # Solar-Temperaturen (wenn CONF_ENABLE_SOLAR_SENSORS)
    30012: {"name": "temp_collector", "description": "Kollektortemperatur", "unit": "°C", "scale": 0.1, "feature": CONF_ENABLE_SOLAR_SENSORS},
    
    # Heizkessel-Temperaturen (wenn CONF_ENABLE_BOILER_SENSORS)
    # Dies sind die Standard-Heizkessel (Modula, PMI, etc.)
    30013: {"name": "temp_boiler_flow", "description": "Kesselvorlauf", "unit": "°C", "scale": 0.1, "feature": CONF_ENABLE_BOILER_SENSORS},
    30014: {"name": "temp_boiler_return", "description": "Kesselrücklauf", "unit": "°C", "scale": 0.1, "feature": CONF_ENABLE_BOILER_SENSORS},
    
    # Holzkessel-Temperaturen (wenn CONF_ENABLE_WOOD_BOILER_SENSORS)
    # SystaComfort Wood Erweiterung für Scheitholzkessel/Kaminofen
    30015: {"name": "temp_wood_boiler_flow", "description": "Kesselvorlauf Holzkessel", "unit": "°C", "scale": 0.1, "feature": CONF_ENABLE_WOOD_BOILER_SENSORS},
    30016: {"name": "temp_wood_boiler_return", "description": "Kesselrücklauf Holzkessel", "unit": "°C", "scale": 0.1, "feature": CONF_ENABLE_WOOD_BOILER_SENSORS},
    30017: {"name": "temp_wood_buffer_top", "description": "Holzkessel Puffer oben", "unit": "°C", "scale": 0.1, "feature": CONF_ENABLE_WOOD_BOILER_SENSORS},
    
    # Pool-Temperaturen (wenn CONF_ENABLE_POOL_SENSORS)
    30020: {"name": "temp_pool", "description": "Schwimmbadtemperatur", "unit": "°C", "scale": 0.1, "feature": CONF_ENABLE_POOL_SENSORS},
    30021: {"name": "temp_pool_flow", "description": "Vorlauftemperatur Schwimmbadheizkreis", "unit": "°C", "scale": 0.1, "feature": CONF_ENABLE_POOL_SENSORS},
    30022: {"name": "temp_pool_return", "description": "Rücklauftemperatur Schwimmbadheizkreis", "unit": "°C", "scale": 0.1, "feature": CONF_ENABLE_POOL_SENSORS},
}

MODBUS_HOLDING_REGISTERS = {
    # Basis-Register (immer verfügbar)
    40001: {"name": "smarthome_type", "description": "Typ Smarthome-System", "read_only": False},
    40002: {"name": "smarthome_error", "description": "Störcode Smarthome-System", "read_only": False},
    40003: {"name": "setpoint_flow_hk1", "description": "Sollvorlauf Heizkreis 1", "unit": "°C", "scale": 0.1, "read_only": False},
    40004: {"name": "setpoint_flow_hk2", "description": "Sollvorlauf Heizkreis 2", "unit": "°C", "scale": 0.1, "read_only": False},
    40009: {"name": "setpoint_dhw", "description": "Sollwert Trinkwasser", "unit": "°C", "scale": 0.1, "read_only": False},
    40010: {"name": "max_flow_temp_hk1", "description": "Maximale Vorlauftemperatur HK1", "unit": "°C", "scale": 0.1, "read_only": True},
    40011: {"name": "max_flow_temp_hk2", "description": "Maximale Vorlauftemperatur HK2", "unit": "°C", "scale": 0.1, "read_only": True},
    
    # Fehler-Register
    40013: {"name": "error_controller", "description": "Störcode Heizungsregler", "read_only": True},
    40014: {"name": "error_solar", "description": "Störcode Solarregler", "read_only": True, "feature": CONF_ENABLE_SOLAR_SENSORS},
    
    # Heizkessel-Fehler (Modula II, NT/III, PMI - wenn CONF_ENABLE_BOILER_SENSORS)
    40015: {"name": "error_boiler_modula2", "description": "Störcode Heizkessel Modula II", "read_only": True, "feature": CONF_ENABLE_BOILER_SENSORS},
    40016: {"name": "error_boiler_modula_nt", "description": "Störcode Heizkessel Modula NT/III", "read_only": True, "feature": CONF_ENABLE_BOILER_SENSORS},
    40017: {"name": "error_boiler_pmi", "description": "Störcode Heizkessel PMI", "read_only": True, "feature": CONF_ENABLE_BOILER_SENSORS},
    
    # Pelletskessel-Fehler (PELLETTI - wenn CONF_ENABLE_PELLET_SENSORS)
    40018: {"name": "error_pellet_3", "description": "Störcode Pelletskessel PELLETTI III", "read_only": True, "feature": CONF_ENABLE_PELLET_SENSORS},
    40019: {"name": "error_pellet_touch", "description": "Störcode Pelletskessel PELLETTI TOUCH/PELEO", "read_only": True, "feature": CONF_ENABLE_PELLET_SENSORS},
    
    # Solar-Register (wenn CONF_ENABLE_SOLAR_SENSORS)
    40020: {"name": "solar_power", "description": "Leistung des Kollektors", "unit": "kW", "scale": 0.1, "read_only": True, "feature": CONF_ENABLE_SOLAR_SENSORS},
    40021: {"name": "solar_energy_today", "description": "Tagesenergie", "unit": "kWh", "read_only": True, "feature": CONF_ENABLE_SOLAR_SENSORS},
    40022: {"name": "solar_energy_total", "description": "Gesamtenergie", "unit": "kWh", "read_only": True, "registers": 2, "feature": CONF_ENABLE_SOLAR_SENSORS},
    
    # Energie-Register (wenn CONF_ENABLE_ENERGY_SENSORS)
    40024: {"name": "energy_dhw", "description": "Wärmemenge Trinkwasser", "unit": "kWh", "read_only": True, "registers": 2, "feature": CONF_ENABLE_ENERGY_SENSORS},
    40026: {"name": "energy_circulation", "description": "Wärmemenge Zirkulation", "unit": "kWh", "read_only": True, "registers": 2, "feature": CONF_ENABLE_ENERGY_SENSORS},
    
    # Heizkessel Betriebsdaten (wenn CONF_ENABLE_BOILER_SENSORS und CONF_ENABLE_ENERGY_SENSORS)
    40028: {"name": "boiler_hours", "description": "Betriebsstunden Heizkessel", "unit": "h", "read_only": True, "registers": 2, "feature": CONF_ENABLE_BOILER_SENSORS},
    40030: {"name": "boiler_starts", "description": "Anzahl Starts Heizkessel", "read_only": True, "registers": 2, "feature": CONF_ENABLE_BOILER_SENSORS},
    
    # Pelletsofen Betriebsdaten (wenn CONF_ENABLE_PELLET_SENSORS)
    40032: {"name": "pellet_hours", "description": "Betriebsstunden Pelletsofen", "unit": "h", "read_only": True, "registers": 2, "feature": CONF_ENABLE_PELLET_SENSORS},
    40034: {"name": "pellet_consumption", "description": "Gesamtpelletverbrauch", "unit": "t", "scale": 0.1, "read_only": True, "feature": CONF_ENABLE_PELLET_SENSORS},
    
    # Status-Register
    40035: {"name": "status_dhw", "description": "Status Warmwasser", "read_only": True},
    40036: {"name": "status_circulation", "description": "Status der Zirkulation", "read_only": True},
    40037: {"name": "status_hk1", "description": "Status Heizkreis 1", "read_only": True},
    40038: {"name": "status_hk2", "description": "Status Heizkreis 2", "read_only": True},
    40040: {"name": "status_solar", "description": "Status Solarregler", "read_only": True, "feature": CONF_ENABLE_SOLAR_SENSORS},
    40041: {"name": "status_pool", "description": "Status Schwimmbadheizkreis", "read_only": True, "feature": CONF_ENABLE_POOL_SENSORS},
    40042: {"name": "status_boiler", "description": "Status Heizkessel", "read_only": True, "feature": CONF_ENABLE_BOILER_SENSORS},
    40043: {"name": "status_pellet", "description": "Status Pelletsofen", "read_only": True, "feature": CONF_ENABLE_PELLET_SENSORS},
    40044: {"name": "status_wood_boiler", "description": "Status Holzkessel/Scheitholzkessel", "read_only": True, "feature": CONF_ENABLE_WOOD_BOILER_SENSORS},
    
    # Sollwerte
    40045: {"name": "setpoint_buffer_top", "description": "Solltemperatur Puffer oben", "unit": "°C", "scale": 0.1, "read_only": True},
    40046: {"name": "setpoint_boiler", "description": "Kesselsolltemperatur", "unit": "°C", "scale": 0.1, "read_only": True, "feature": CONF_ENABLE_BOILER_SENSORS},
}

# Status mappings (basierend auf Paradigma Dokumentation)
DHW_STATUS_MAP = {
    0: "Kein Bedarf",
    1: "Wird beladen",
    2: "Frostschutz aktiv",
    3: "Bedarf, aber gesperrt",
    4: "Nachlaufzeit",
    5: "Zu warm",
    6: "Warten auf Wasserentnahme",
    7: "Wasserentnahme",
    8: "Inbetriebnahme",
    9: "Manueller Betrieb",
    10: "Betrieb Zirkulation",
    11: "Nachlauf Zirkulation",
    12: "Zirkulation in Sperrzeit",
    13: "Durch Smarthome gesperrt",
}

CIRCULATION_STATUS_MAP = {
    0: "Nicht verwendet",
    1: "Nachlauf",
    2: "Gesperrt",
    3: "Aus",
    4: "Durch Temperaturfühler gesperrt",
    5: "An",
    6: "Frostschutz an",
    7: "Durch Smarthome gesperrt",
}

HEATING_CIRCUIT_STATUS_MAP = {
    0: "Aus",
    1: "Heizbetrieb",
    2: "Anschieben",
    3: "Vorhaltezeit",
    4: "Gesperrt",
    5: "Messung (Inbetriebnahme)",
    6: "Frostschutz",
    7: "Aufheizprogramm Estrich",
    8: "Überschusswärme abführen",
    9: "Manueller Betrieb",
    10: "Notbetrieb",
    11: "Nicht installiert",
    12: "Kühlkreis aktiv",
}

SOLAR_STATUS_MAP = {
    0: "Wartet auf Sonne",
    1: "Frostschutz",
    2: "Anschieben",
    3: "Einschaltverzögerung",
    4: "Erwärmt Speicher",
    5: "Speicher voll",
    6: "Kollektor überhitzt",
    7: "Manueller Betrieb",
    8: "Messung",
    9: "Notbetrieb",
}

BOILER_STATUS_MAP = {
    0: "Aus",
    1: "An",
    2: "Bereitet Warmwasser",
    3: "Für Heizkreis an",
    4: "Belädt Pufferspeicher",
    5: "Gesperrt",
    6: "Wärmepumpe kühlt",
    7: "Bereitet Warmwasser (Combi)",
}

PELLET_STATUS_MAP = {
    0: "Aus",
    1: "Standby",
    2: "Anheizphase",
    3: "Leistungsbrand",
    4: "Testet Abgasklappe",
    5: "Nachlauf",
    6: "Reinigung",
    7: "Störung",
    8: "Unbekannter Status",
}

WOOD_BOILER_STATUS_MAP = {
    0: "Nicht gefunden",
    1: "Aus",
    2: "Anheizen",
    3: "Leistungsbrand",
    4: "Ausbrand",
    5: "Nachkühlen",
    6: "Schaltet ab",
    7: "Anschieben",
}

POOL_STATUS_MAP = {
    0: "Nicht gefunden",
    1: "Aus",
    2: "Gesperrt",
    3: "Warm genug",
    4: "Frostschutz",
    5: "Erwärmung Normal",
    6: "Erwärmung Komfort",
    7: "Solare Überschusswärme",
    8: "Gesperrt (Puffer zu kalt)",
    9: "Gesperrt (Warmwasser)",
    10: "Kühlen",
}