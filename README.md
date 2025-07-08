[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Refoss LAN
- Home Assistant version: 2025.2.5 or above

## Installation & configuration
You can install this component in two ways: via HACS or manually.
HACS is a nice community-maintained components manager, which allows you to install git-hub hosted components in a few clicks.
If you have already HACS installed on your HomeAssistant, it's better to go with that.
On the other hand, if you don't have HACS installed or if you don't plan to install it, then you can use manual installation.

### Option A: Installing via HACS
If you have HACS, well, it's piece of cake!
Just search for "Refoss" (Full name is Refoss LAN) in the default repository of HACS and it'll show up.
Click on Install. When the installation completes, **you must restart homeassistant** in order to make it work.
As soon as HomeAssistant is restarted, you can proceed with __component setup__.

### Option B: Classic installation (custom_component)
1. Download the latest zip release archive from [here](https://github.com/Refoss/refoss-homeassistant/releases/latest)
1. Unzip/copy the refoss_lan directory within the `custom_components` directory of your homeassistant installation.
   The `custom_components` directory resides within your homeassistant configuration directory.
   Usually, the configuration directory is within your home (`~/.homeassistant/`).
   In other words, the configuration directory of homeassistant is where the config.yaml file is located.
   After a correct installation, your configuration directory should look like the following.
    ```
    └── ...
    └── configuration.yaml
    └── secrects.yaml
    └── custom_components
        └── refoss_lan
            └── __init__.py
            └── entity.py
            └── switch.py
            └── ...
    ```

   **Note**: if the custom_components directory does not exist, you need to create it.

After copy-pasting the refoss_lan directory into the custom_components folder, you need to restart HomeAssistant.
As soon as HomeAssistant is restarted, you can proceed with __component setup__.

## Configuration
- In the HA UI go to "Configuration" -> "Integrations", click "+", search for "Refoss LAN", and select the "Refoss LAN" integration from the list.
  Or click here: [![Start Config Flow](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=refoss_lan)

## Supported device models

| Model                               | Version            |             
|-------------------------------------|--------------------|
| `Refoss Smart Wi-Fi Switch, R10`    | `all`              |
| `Refoss Smart Energy Monitor, EM06` | `v2.3.8 and above` |
| `Refoss Smart Energy Monitor, EM16` | `v3.1.7 and above` |

## Tips
- When Home Assistant runs in a virtual machine, Please set the virtual machine's network to bridge mode.
- Refoss LAN and Refoss(core integration) cannot be used simultaneously. If you plan to use Refoss LAN, please remove Refoss first.