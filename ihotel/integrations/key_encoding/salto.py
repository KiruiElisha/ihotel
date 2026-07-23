# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Salto ProAccess Space / SHIP adapter (scaffold).

Salto exposes room-key operations through the ProAccess Space REST API and,
for on-site encoders, the SHIP protocol. This adapter is wired for the REST
flow: it reads the endpoint and credentials from settings and shapes the
request/response. The vendor-specific field names must be confirmed against
the property's ProAccess Space version before going live, so ``encode`` raises
a clear error until that verification is done and the guard is removed.
"""

from __future__ import annotations

from frappe.utils import now_datetime

from .base import EncodeRequest, EncodeResult, EncoderError, KeyEncoder


class SaltoAdapter(KeyEncoder):
	vendor = "Salto"

	def _client(self):
		import requests  # local import: only needed when a real vendor is used

		endpoint = self.config.get("endpoint")
		api_key = self.config.get("api_key")
		if not endpoint or not api_key:
			raise EncoderError(
				"Salto is selected but its endpoint/credentials are not set in "
				"iHotel Settings → Card Integration."
			)
		session = requests.Session()
		session.headers.update({"Authorization": f"Bearer {api_key}"})
		return session, endpoint.rstrip("/")

	def encode(self, request: EncodeRequest) -> EncodeResult:
		request.validate()
		session, endpoint = self._client()
		payload = {
			"roomId": request.room,
			"validFrom": request.valid_from.isoformat(),
			"validUntil": request.valid_to.isoformat(),
			"accessLevel": request.access_level,
			"guestName": request.guest_name,
			"reference": request.reference,
			"addKey": request.is_duplicate,  # add without invalidating prior keys
			"commonDoors": request.common_doors,
		}
		# The exact route ("/api/v1/keys" here) and response schema depend on
		# the ProAccess Space version; confirm before removing this guard.
		raise EncoderError(
			"Salto adapter is scaffolded but not yet verified against this "
			"property's ProAccess Space instance. Confirm the API route and "
			"payload, then enable it in salto.py."
		)
		# Reference implementation once verified:
		# resp = session.post(f"{endpoint}/api/v1/keys", json=payload, timeout=20)
		# resp.raise_for_status()
		# data = resp.json()
		# return EncodeResult(
		#     card_uid=data["keyId"],
		#     vendor=self.vendor,
		#     encoded_at=now_datetime(),
		#     raw=data,
		#     mobile_key_token=data.get("mobileKey"),
		# )

	def cancel(self, card_uid: str) -> None:
		session, endpoint = self._client()
		resp = session.delete(f"{endpoint}/api/v1/keys/{card_uid}", timeout=20)
		if resp.status_code not in (200, 202, 204, 404):
			raise EncoderError(f"Salto refused to cancel key {card_uid}: {resp.text}")
