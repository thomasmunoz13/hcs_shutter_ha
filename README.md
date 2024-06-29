# HCS Shutter Home Assistant Integration

This is a Home Assistant integration for controlling a shutter roller using HACS.

## Installation

To install this integration, follow these steps:

1. Open your Home Assistant configuration directory.
2. If you don't have a `custom_components` directory, create one.
3. Copy the `hcs_shutter` directory from this repository into the `custom_components` directory.
4. Add the following configuration to your `configuration.yaml` file:

```yaml
shutter_roller:
    covers:
      - name: Foo
        host: 192.168.1.100
```

5. Restart Home Assistant to apply the changes.

## Usage

Once the integration is installed and configured, you can control the shutter roller through the Home Assistant user interface or using automations and scripts.


## License

This project is licensed under the [MIT License](https://github.com/thomasmunoz13/hcs_shutter_ha/blob/main/LICENSE).
