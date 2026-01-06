# SystaSmartC2 Home Assistant Integration

Custom integration for Paradigma SystaSmartC2 heating controller via Modbus TCP.

## Features
- Full monitoring of temperatures, buffer, hot water, circulation, heating circuits
- Dynamic detection of components (hot water, solar, boiler, wood boiler)
- Climate entities for heating circuits
- Water heater entity for hot water control
- Services for temperature setting
- Support for optional wood boiler

## Installation
1. Use HACS:
   - HACS → Integrations → Three dots → Custom repositories
   - Repository: 
   - Category: Integration
   - Install

2. Restart Home Assistant
3. Add via UI: Settings → Devices & Services → + Add → SystaSmartC2

## Configuration
- Host: IP of your SystaSmartC2
- Port: 502
- Slave ID: 1

The integration detects components and offers options.

## Services
- `systasmartc2.set_heating_temperature`: Set heating circuit temperature
- `systasmartc2.set_dhw_temperature`: Set hot water temperature
- `systasmartc2.control_dhw`: Enable/disable hot water

## Dashboard Example
See `examples/heizung_dashboard.yaml` for a Mushroom Cards example.

## Known Issues
- Energy counters may be unavailable on some heat pump setups.

## Contributing
Pull requests welcome!

License: MIT