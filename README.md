

# Cuby Gas Level (Home Assistant) 
<img width="256" height="256" alt="icon" src="https://github.com/user-attachments/assets/722d358e-1d17-43e7-b5a0-d74a6580e702" />


Custom integration to display [Cuby Helios](https://cuby.mx/collections/cuby/products/cuby-helios-pro-medidor-gas-lp) gas level history for one or more devices. Includes:
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

## Screenshots
<img width="1789" height="475" alt="image (2)" src="https://github.com/user-attachments/assets/54f0a734-6e3e-4faa-8aaa-e7a3955e7262" />

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
