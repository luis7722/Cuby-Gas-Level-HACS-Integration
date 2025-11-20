# Cuby Gas Level (Home Assistant)

Custom integration to display Cuby Smart gas level history for one or more devices. Includes:
- Config Flow (UI) for credentials and device IDs
- Automatic token acquisition and refresh
- DataUpdateCoordinator polling
- One sensor per device

## Installation (HACS)
1. Add this repository in HACS as a custom repository (Integration).
2. Install "Cuby Gas Level".
3. Restart Home Assistant.
4. Go to Settings → Devices & Services → Add Integration → search "Cuby Gas Level".
5. Enter email, password, and Cuby device IDs (comma-separated).

## Lovelace examples

```yaml
type: gauge
entity: sensor.cuby_gas_level_ABC123
min: 0
max: 100
name: Gas Level ABC123
type: entities
title: Cuby Gas Devices
entities:
  - sensor.cuby_gas_level_ABC123
  - sensor.cuby_gas_level_XYZ789