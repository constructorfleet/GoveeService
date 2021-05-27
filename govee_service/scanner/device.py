import logging
from typing import Optional, Set, Tuple, Type

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
        _LOGGER.debug(f"{device} {device.rssi}")

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


class LedDevice(Device):
    SUPPORTED_MODELS = {"H6170"}

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
        pass

    async def set_color(self,
                        color: Tuple[int, int, int]) -> None:
        pass

    async def set_brightness(self,
                             brightness: int) -> None:
        pass

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
