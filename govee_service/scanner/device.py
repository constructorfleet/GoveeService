import logging
from typing import Optional, Set, Tuple, Type, Union, List

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from .helpers import get_govee_model

_LOGGER = logging.getLogger(__name__)


class Device:
    SUPPORTED_MODELS: Set[str] = None

    def __init__(
            self,
            device: BLEDevice,
            advertisement: Optional[AdvertisementData] = None
    ) -> None:
        """Initialize a device."""
        self._device = device
        self._model = get_govee_model(device.name)
        if advertisement:
            self.update(device, advertisement)
        _LOGGER.info(f"{device} {device.rssi}")

    @property
    def address(self) -> str:
        """Return the address of this device."""
        return self._device.address

    @property
    def name(self) -> str:
        """Return the name of this device."""
        return self._device.name

    @property
    def rssi(self) -> int:
        """Return the rssi of this device."""
        return self._device.rssi

    @property
    def model(self) -> str:
        """Return the model of this device."""
        return self._model

    def update(self,
               device: BLEDevice,
               advertisement: AdvertisementData) -> None:
        raise NotImplementedError()

    def update_device(self,
                      device: BLEDevice) -> None:
        if self._device != device:
            self._device = device

    async def _send(self,
                    command: int,
                    payload: Union[bytes, List[int]]) -> None:

        cmd = command & 0xFF
        payload = bytes(payload)
        frame = bytes([0x33, cmd]) + bytes(payload)
        # pad frame data to 19 bytes (plus checksum)
        frame += bytes([0] * (19 - len(frame)))

        # The checksum is calculated by XORing all data bytes
        checksum = 0
        for b in frame:
            checksum ^= b

        frame += bytes([checksum & 0xFF])

        async with BleakClient(self.address) as client:
            await client.write_gatt_char('00010203-0405-0607-0809-0a0b0c0d2b11', frame)


class LedDevice(Device):
    SUPPORTED_MODELS = {"H6170"}
    COMMAND_POWER = 0x01
    COMMAND_COLOR = 0x05
    COMMAND_BRIGHTNESS = 0x04

    MANUAL_COLOR = 0x02

    _brightness = 0
    _color = (0, 0, 0)
    _on = False

    @property
    def brightness(self) -> int:
        return self._brightness

    @property
    def color(self) -> Tuple[int, int, int]:
        return self._color

    @property
    def is_on(self) -> bool:
        return self._on

    async def turn_on(self) -> None:
        await send(self,
                   self.COMMAND_POWER,
                   [0x1])

    async def turn_off(self) -> None:
        await send(self,
                   self.COMMAND_POWER,
                   [0x0])

    async def set_color(self,
                        color: Tuple[int, int, int]) -> None:
        await send(self,
                   self.COMMAND_COLOR,
                   [self.MANUAL_COLOR, *color])

    async def set_brightness(self,
                             brightness: int) -> None:
        await send(self,
                   self.COMMAND_BRIGHTNESS,
                   [round((brightness / 100) * 0xFF)])

    def update(self, device: BLEDevice,
               advertisement: AdvertisementData) -> None:
        pass


VALID_CLASSES: Set[Type[Device]] = {LedDevice}
MODEL_MAP = {model: cls for cls in VALID_CLASSES for model in cls.SUPPORTED_MODELS}


def determine_known_device(
        device: BLEDevice,
        advertisement: Optional[AdvertisementData] = None
) -> Optional[Device]:
    model = get_govee_model(device.name)
    if model in MODEL_MAP:
        return MODEL_MAP[model](device, advertisement)
    elif model and advertisement.manufacturer_data:
        _LOGGER.warning(
            "%s appears to be a Govee %s, but no handler has been created",
            device.name,
            model,
        )
    return None
