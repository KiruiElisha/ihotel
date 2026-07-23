# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Pluggable electronic room-key encoding.

Every lock vendor speaks a different protocol, so the app talks to a single
:class:`~ihotel.integrations.key_encoding.base.KeyEncoder` interface and the
vendor-specific details live behind adapters. :func:`get_encoder` reads
``iHotel Settings`` and returns the adapter configured for the property.

The ``mock`` adapter is fully functional and is what the app uses until a real
lock system is configured, so check-in works end to end today.
"""

from __future__ import annotations

from .base import EncodeRequest, EncodeResult, KeyEncoder, EncoderError
from .registry import ENCODERS, get_encoder

__all__ = [
	"EncodeRequest",
	"EncodeResult",
	"KeyEncoder",
	"EncoderError",
	"ENCODERS",
	"get_encoder",
]
