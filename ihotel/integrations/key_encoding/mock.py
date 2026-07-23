# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""A fully working in-software key encoder.

This is the default until a real lock system is configured. It "encodes" a key
by minting a deterministic-looking UID and recording it, so the whole check-in
→ issue-key → cancel-key flow works and can be demoed and tested without any
hardware. It never touches an external system.
"""

from __future__ import annotations

import hashlib

import frappe
from frappe.utils import now_datetime

from .base import EncodeRequest, EncodeResult, KeyEncoder


class MockEncoder(KeyEncoder):
	vendor = "Mock"

	def encode(self, request: EncodeRequest) -> EncodeResult:
		request.validate()
		# A stable, unique-enough UID: room + validity + a short random-ish
		# suffix from the frappe hash so repeated encodes differ.
		seed = f"{request.room}|{request.valid_from.isoformat()}|{frappe.generate_hash(length=8)}"
		uid = "MOCK-" + hashlib.sha1(seed.encode()).hexdigest()[:12].upper()
		return EncodeResult(
			card_uid=uid,
			vendor=self.vendor,
			encoded_at=now_datetime(),
			raw={
				"simulated": True,
				"room": request.room,
				"access_level": request.access_level,
				"is_duplicate": request.is_duplicate,
			},
		)

	def cancel(self, card_uid: str) -> None:
		# Nothing to talk to; cancellation always "succeeds".
		return None
