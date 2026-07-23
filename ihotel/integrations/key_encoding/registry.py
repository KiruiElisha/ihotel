# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Resolve the configured key encoder from iHotel Settings."""

from __future__ import annotations

import frappe

from .assa_abloy import AssaAbloyAdapter
from .base import KeyEncoder
from .mock import MockEncoder
from .onity import OnityAdapter
from .salto import SaltoAdapter

# Vendor value (as stored on iHotel Settings) → adapter class.
ENCODERS: dict[str, type[KeyEncoder]] = {
	"Mock": MockEncoder,
	"Salto": SaltoAdapter,
	"Assa Abloy": AssaAbloyAdapter,
	"Onity": OnityAdapter,
}


def _settings_config() -> tuple[str, dict]:
	"""Read the encoder vendor and its connection config from iHotel Settings."""
	settings = frappe.get_cached_doc("iHotel Settings")
	vendor = getattr(settings, "key_encoder_vendor", None) or "Mock"
	config = {
		"endpoint": getattr(settings, "key_encoder_endpoint", None),
		"facility_id": getattr(settings, "key_encoder_facility_id", None),
		# Password fields must be read decrypted.
		"api_key": settings.get_password("key_encoder_api_key", raise_exception=False)
		if hasattr(settings, "get_password")
		else None,
	}
	return vendor, config


def get_encoder(vendor: str | None = None, config: dict | None = None) -> KeyEncoder:
	"""Return an encoder instance.

	With no arguments, reads the vendor and config from iHotel Settings. Pass
	``vendor``/``config`` explicitly for tests or one-off use. Falls back to the
	mock encoder for an unknown vendor so check-in never hard-fails on a
	mis-typed setting.
	"""
	if vendor is None:
		vendor, resolved = _settings_config()
		config = config or resolved

	adapter_cls = ENCODERS.get(vendor, MockEncoder)
	return adapter_cls(config or {})
