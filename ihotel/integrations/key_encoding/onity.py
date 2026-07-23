# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Onity DirectKey / encoder adapter (scaffold).

Onity properties typically encode through a local encoder station driven by
Onity's middleware, with DirectKey for mobile credentials. Because the encoder
is usually a LAN device rather than a public cloud API, this adapter points at
a middleware endpoint on the property network. It is scaffolded but guarded
until verified against the site's Onity installation.
"""

from __future__ import annotations

from frappe.utils import now_datetime

from .base import EncodeRequest, EncodeResult, EncoderError, KeyEncoder


class OnityAdapter(KeyEncoder):
	vendor = "Onity"

	def _endpoint(self) -> str:
		endpoint = self.config.get("endpoint")
		if not endpoint:
			raise EncoderError(
				"Onity is selected but the encoder/middleware endpoint is not set "
				"in iHotel Settings → Card Integration."
			)
		return endpoint.rstrip("/")

	def encode(self, request: EncodeRequest) -> EncodeResult:
		request.validate()
		endpoint = self._endpoint()
		payload = {
			"room": request.room,
			"checkIn": request.valid_from.isoformat(),
			"checkOut": request.valid_to.isoformat(),
			"level": request.access_level,
			"duplicate": request.is_duplicate,
			"doors": request.common_doors,
		}
		raise EncoderError(
			"Onity adapter is scaffolded but not yet verified against this "
			"property's encoder/middleware. Confirm the local endpoint and "
			"payload, then enable it in onity.py."
		)
		# Reference implementation once verified:
		# import requests
		# resp = requests.post(f"{endpoint}/encode", json=payload, timeout=20)
		# resp.raise_for_status()
		# data = resp.json()
		# return EncodeResult(
		#     card_uid=data["cardId"], vendor=self.vendor,
		#     encoded_at=now_datetime(), raw=data,
		# )

	def cancel(self, card_uid: str) -> None:
		endpoint = self._endpoint()
		import requests

		resp = requests.post(f"{endpoint}/cancel", json={"cardId": card_uid}, timeout=20)
		if resp.status_code not in (200, 202, 204, 404):
			raise EncoderError(f"Onity refused to cancel key {card_uid}: {resp.text}")
