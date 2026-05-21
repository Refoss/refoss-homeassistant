[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Refoss LAN

Local LAN integration for Refoss smart devices — no cloud dependency. Provides switch control and energy monitoring.

**Minimum Home Assistant version: 2025.2.5**

## Features

- **Switch control** — on/off/toggle for each channel
- **Energy monitoring** — power, voltage, current, power factor, and monthly energy consumption (EM06/EM16)

## Installation

### Option A: Via HACS

1. Search for **"Refoss LAN"** in the HACS default repository and click **Install**.
2. **Restart Home Assistant**.
3. Proceed to [Configuration](#configuration).

### Option B: Manual installation

1. Download the latest release from [GitHub Releases](https://github.com/Refoss/refoss-homeassistant/releases/latest).
2. Copy the `refoss_lan` directory into the `custom_components` folder of your Home Assistant configuration directory:

   ```
   ├── configuration.yaml
   ├── secrets.yaml
   └── custom_components
       └── refoss_lan
           ├── __init__.py
           ├── config_flow.py
           ├── const.py
           ├── coordinator.py
           ├── entity.py
           ├── manifest.json
           ├── sensor.py
           ├── switch.py
           └── ...
   ```

   If the `custom_components` directory does not exist, create it.

3. **Restart Home Assistant**.
4. Proceed to [Configuration](#configuration).

## Configuration

1. In Home Assistant, go to **Settings → Devices & Services**, click **Add Integration**, and search for **"Refoss LAN"**.
2. Enter the **device IP address** and **update interval** (in seconds, minimum 1).
3. The integration will discover the device on your local network and create the corresponding entities.

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=refoss_lan)

## Supported devices

| Model | Firmware | Entities |
|---|---|---|
| Refoss Smart Wi-Fi Switch (R10) | All versions | Switch |
| Refoss Smart Energy Monitor (EM06) | v2.3.8+ | Switch, Energy Sensors |
| Refoss Smart Energy Monitor (EM16) | v3.1.7+ | Switch, Energy Sensors |

## Requirements

- **Home Assistant and the device must be on the same local network.**
- **VMware/ESXi**: Set the virtual machine network adapter to **bridged** mode.
- **Docker**: Set the container network to **host** mode.
- **Refoss LAN and the Refoss core integration cannot be used simultaneously.** If you plan to use Refoss LAN, remove the Refoss core integration first.

## Tips

- If your device is one of the following models, please use [Refoss RPC](https://github.com/Refoss/refoss_rpc) instead:

  | Model | Firmware |
  |---|---|
  | Refoss Smart Wi-Fi Switch (R11) | All versions |
  | Refoss Smart Wi-Fi Plug (P11S) | All versions |
  | Refoss Smart Wi-Fi Switch (R21) | All versions |
  | Refoss Smart Energy Monitor (EM06P) | All versions |
  | Refoss Smart Energy Monitor (EM16P) | All versions |
