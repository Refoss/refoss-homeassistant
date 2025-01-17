# Refoss LAN

- Revision Date: January 17, 2025
- Revised Version: v1.0.2
- Revision Focus: Support for filling in device IP for integration
- Integration Type: Changed from hub to device
- Version Description:
  - v1.0.1: If the user does not know the device IP, the device will be automatically discovered after launching the Refoss Lan integration, but the device and Home Assistant need to be on the same network.
  - v1.0.2: Support for filling in device IP for integration.


## Installation

### Custom Repositories in HACS (recommended)
- Make sure the [HACS integration](https://hacs.xyz/) is properly installed for your instance of home assistant.
- Reference [Custom Repositories](https://hacs.xyz/docs/faq/custom_repositories),In the HACS UI go to "Integrations", click on "+" in the lower right corner".
- Paste https://github.com/Refoss/refoss-homeassistant into the field that says "Add custom repository URL", select "Integration" from "Category" dropdown and click "Add".
- You should now see a card with the Refoss LAN integration in the HACS -> "Integrations" section. Click "Install".
- Select the latest version from the dropdown and click "Install".
- Restart Home Assistant.

### Manual installation
- Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).
- If you do not have a custom_components directory (folder) there, you need to create it.
- In the custom_components directory (folder) create a new folder called refoss_lan.
- Download all the files from the custom_components/refoss_lan/ directory (folder) in this repository.
- Place the files you downloaded in the new directory (folder) you created.
- Restart Home Assistant.

## Configuration
- In the HA UI go to "Configuration" -> "Integrations", click "+", search for "Refoss LAN", and select the "Refoss LAN" integration from the list.
  Or click here: [![Start Config Flow](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=refoss_lan)

## Supported device models

| Model                               | Version            |             
|-------------------------------------|--------------------|
| `Refoss Smart Wi-Fi Switch, R10`    | `all`              |
| `Refoss Smart Energy Monitor, EM06` | `v2.3.8 and above` |
| `Refoss Smart Energy Monitor, EM16` | `v3.1.7 and above` |

