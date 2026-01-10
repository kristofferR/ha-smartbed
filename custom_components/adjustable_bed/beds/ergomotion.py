"""Ergomotion bed controller - now part of Keeson.

Ergomotion beds use the same protocol as Keeson BaseI4/BaseI5 with position feedback.
This module is kept for backward compatibility - new code should use KeesonController
with variant="ergomotion".
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .keeson import KeesonCommands, KeesonController

if TYPE_CHECKING:
    from ..coordinator import AdjustableBedCoordinator

# Backward compatibility aliases
ErgomotionCommands = KeesonCommands


def int_to_bytes_le(value: int) -> list[int]:
    """Convert an integer to 4 bytes (little-endian)."""
    return [
        value & 0xFF,
        (value >> 8) & 0xFF,
        (value >> 16) & 0xFF,
        (value >> 24) & 0xFF,
    ]


def crc(data: bytes) -> int:
    """Calculate CRC checksum (inverted sum)."""
    return (~sum(data)) & 0xFF


class ErgomotionController(KeesonController):
    """Controller for Ergomotion beds (backward compatibility wrapper).

    Ergomotion beds are now handled by KeesonController with the 'ergomotion' variant.
    This class is kept for backward compatibility only.
    """

    def __init__(self, coordinator: AdjustableBedCoordinator) -> None:
        """Initialize the Ergomotion controller.

        Args:
            coordinator: The AdjustableBedCoordinator instance
        """
        super().__init__(coordinator, variant="ergomotion")
