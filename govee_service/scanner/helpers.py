import logging
from typing import Optional, Tuple

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

_LOGGER = logging.getLogger(__name__)


def get_govee_model(name: str) -> Optional[str]:
    if not name:
        return None
    elif name.startswith(("ihoment_", "Govee_", "Minger_", "GBK_")):
        split = name.split("_")
        return split[1] if len(split) == 3 else None
    elif name.startswith("GVH"):
        split = name.split("_")
        return split[0][2:] if len(split) > 1 else None
    return None


def int_to_hex(val: int) -> str:
    h = hex(val).replace("0x", "")
    while len(h) < 2:
        h = "0" + h
    return h


def rgb_hex(red: int,
            green: int,
            blue: int) -> str:
    sig = (3*16 + 1) ^ red ^ green ^ blue
    bins = [51, 5, 2, red, green, blue, 0, 255, 174, 84, 0, 0, 0, 0, 0, 0, 0, 0, 0, sig]
    bins_str = map(int_to_hex, bins)
    return "".join(bins_str)


def brightness_hex(brightness: int) -> str:
    sig = (3*16 + 3) ^ 4 ^ brightness
    bins = [51, 4, brightness, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, sig]
    bins_str = map(int_to_hex, bins)
    return "".join(bins_str)


# def decode_temperature_and_humidity(data_packet: bytes) -> Tuple[float, float]:
#     """Decode the temperature and humidity values from a BLE advertisement data packet."""
#     # Adapted from: https://github.com/Thrilleratplay/GoveeWatcher/issues/2
#     packet_value = int(data_packet.hex(), 16)
#     multiplier = 1
#     if packet_value & 0x800000:
#         packet_value = packet_value ^ 0x800000
#         multiplier = -1
#     return float(packet_value / 10000 * multiplier), float(packet_value % 1000 / 10)


def twos_complement(
        n: int,
        w: int = 16) -> int:
    """Two's complement integer conversion."""
    # Adapted from: https://stackoverflow.com/a/33716541.
    if n & (1 << (w - 1)):
        n = n - (1 << w)
    return n


def log_advertisement_message(
        device: BLEDevice,
        advertisement: AdvertisementData
) -> None:
    """Log an advertisement message from a BLE device."""
    _LOGGER.info('Device advertised')
    if get_govee_model(device.name) and advertisement.manufacturer_data:
        _LOGGER.info(
            "Advertisement message from %s (name=%s): %s",
            device.address,
            device.name,
            {k: v.hex() for k, v in advertisement.manufacturer_data.items()},
        )
