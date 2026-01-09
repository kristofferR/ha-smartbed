"""Fixtures for Smart Bed tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

# Enable custom component loading
pytest_plugins = "pytest_homeassistant_custom_component"

from custom_components.smartbed.const import (
    BED_TYPE_LINAK,
    CONF_BED_TYPE,
    CONF_DISABLE_ANGLE_SENSING,
    CONF_HAS_MASSAGE,
    CONF_MOTOR_COUNT,
    CONF_PREFERRED_ADAPTER,
    DOMAIN,
    LINAK_CONTROL_SERVICE_UUID,
)

# Test constants
TEST_ADDRESS = "AA:BB:CC:DD:EE:FF"
TEST_NAME = "Test Bed"


@pytest.fixture
def mock_config_entry_data() -> dict:
    """Return mock config entry data."""
    return {
        CONF_ADDRESS: TEST_ADDRESS,
        CONF_NAME: TEST_NAME,
        CONF_BED_TYPE: BED_TYPE_LINAK,
        CONF_MOTOR_COUNT: 2,
        CONF_HAS_MASSAGE: False,
        CONF_DISABLE_ANGLE_SENSING: True,
        CONF_PREFERRED_ADAPTER: "auto",
    }


@pytest.fixture
def mock_config_entry(hass: HomeAssistant, mock_config_entry_data: dict) -> MockConfigEntry:
    """Return a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TEST_NAME,
        data=mock_config_entry_data,
        unique_id=TEST_ADDRESS,
        entry_id="test_entry_id",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_bleak_client() -> MagicMock:
    """Mock BleakClient."""
    from bleak import BleakClient

    client = MagicMock(spec=BleakClient)
    client.is_connected = True
    client.address = TEST_ADDRESS
    client.mtu_size = 23
    client.services = MagicMock()
    client.services.__iter__ = lambda self: iter([])
    client.services.__len__ = lambda self: 0

    client.connect = AsyncMock(return_value=True)
    client.disconnect = AsyncMock()
    client.write_gatt_char = AsyncMock()
    client.start_notify = AsyncMock()
    client.stop_notify = AsyncMock()

    return client


@pytest.fixture
def mock_bluetooth_service_info() -> MagicMock:
    """Return mock Bluetooth service info for a Linak bed."""
    service_info = MagicMock()
    service_info.name = TEST_NAME
    service_info.address = TEST_ADDRESS
    service_info.rssi = -60
    service_info.manufacturer_data = {}
    service_info.service_data = {}
    service_info.service_uuids = [LINAK_CONTROL_SERVICE_UUID]
    service_info.source = "local"
    service_info.device = MagicMock()
    service_info.advertisement = MagicMock()
    service_info.connectable = True
    service_info.time = 0
    service_info.tx_power = None
    return service_info


@pytest.fixture
def mock_bluetooth_service_info_unknown() -> MagicMock:
    """Return mock Bluetooth service info for an unknown device."""
    service_info = MagicMock()
    service_info.name = "Unknown Device"
    service_info.address = "11:22:33:44:55:66"
    service_info.rssi = -70
    service_info.manufacturer_data = {}
    service_info.service_data = {}
    service_info.service_uuids = ["00001800-0000-1000-8000-00805f9b34fb"]  # Generic Access
    service_info.source = "local"
    service_info.device = MagicMock()
    service_info.advertisement = MagicMock()
    service_info.connectable = True
    service_info.time = 0
    service_info.tx_power = None
    return service_info


@pytest.fixture
def mock_establish_connection(mock_bleak_client: MagicMock) -> Generator[AsyncMock, None, None]:
    """Mock bleak_retry_connector.establish_connection."""
    with patch(
        "custom_components.smartbed.coordinator.establish_connection",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = mock_bleak_client
        yield mock


@pytest.fixture
def mock_async_ble_device_from_address() -> Generator[MagicMock, None, None]:
    """Mock bluetooth.async_ble_device_from_address."""
    with patch(
        "custom_components.smartbed.coordinator.bluetooth.async_ble_device_from_address"
    ) as mock:
        device = MagicMock()
        device.address = TEST_ADDRESS
        device.name = TEST_NAME
        device.details = {"source": "local"}
        mock.return_value = device
        yield mock


@pytest.fixture
def mock_bluetooth_adapters() -> Generator[None, None, None]:
    """Mock bluetooth adapter functions."""
    patches = [
        patch(
            "custom_components.smartbed.coordinator.bluetooth.async_scanner_count",
            return_value=1,
        ),
        patch(
            "custom_components.smartbed.coordinator.bluetooth.async_discovered_service_info",
            return_value=[],
        ),
        patch(
            "custom_components.smartbed.coordinator.bluetooth.async_last_service_info",
            return_value=None,
        ),
    ]

    # Try to patch async_register_connection_params if it exists
    try:
        from homeassistant.components import bluetooth
        if hasattr(bluetooth, 'async_register_connection_params'):
            patches.append(
                patch(
                    "custom_components.smartbed.coordinator.bluetooth.async_register_connection_params",
                )
            )
    except ImportError:
        pass

    with patch.multiple("custom_components.smartbed.coordinator", HAS_CONNECT_PARAMS=False):
        for p in patches:
            p.start()
        try:
            yield
        finally:
            for p in patches:
                p.stop()


@pytest.fixture
def mock_coordinator_connected(
    mock_establish_connection: AsyncMock,
    mock_async_ble_device_from_address: MagicMock,
    mock_bluetooth_adapters: None,
) -> Generator[None, None, None]:
    """Provide all mocks needed for a connected coordinator."""
    yield
