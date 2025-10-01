# Luxor Lighting for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant custom integration for Luxor ZD/ZDC/ZDTWO lighting controllers by Hunter.

## Features

- 🔍 Automatic controller discovery and type detection
- 💡 Monochrome light groups with brightness control
- 🎨 Color light groups with hue/saturation control (ZDC/ZDTWO)
- 🎭 Theme activation via button entities
- 🔄 Automatic polling every 5 minutes
- ⚙️ Easy configuration through UI

## Supported Controllers

- Luxor ZD (Zoning/Dimming)
- Luxor ZDC (Zoning/Dimming/Color)
- Luxor ZDTWO (Zoning/Dimming/Color)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL: `https://github.com/pvandagriff/luxor-homeassistant`
5. Select category: "Integration"
6. Click "Add"
7. Find "Luxor Lighting" in HACS and install
8. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/luxor` folder to your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Luxor"
4. Enter your Luxor controller IP address
5. Optional: Add a name prefix for multi-controller setups
6. Click Submit

## Credits

Based on the Hubitat integration by Russell Goldin (tagyoureit).

## License

Apache License 2.0
