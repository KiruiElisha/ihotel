# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Assa Abloy Hospitality (Vostio / Visionline) adapter (scaffold).

Assa Abloy's cloud platform Vostio (successor to Visionline) exposes a REST API
for issuing physical and mobile keys against a facility. This adapter reads the
facility id and OAuth credentials from settings; the exact token endpoint and
key routes vary by deployment, so ``encode`` raises a clear error until the
integration is verified against the property's tenant.
"""

from __future__ import annotations

from frappe.utils import now_datetime

from .base import EncodeRequest, EncodeResult, EncoderError, KeyEncoder


class AssaAbloyAdapter(KeyEncoder):
	vendor = "Assa Abloy"

	def _config(self):
		endpoint = self.config.get("endpoint")
		api_key = self.config.get("api_key")
		facility = self.config.get("facility_id")
		if not (endpoint and api_key and facility):
			raise EncoderError(
				"Assa Abloy is selected but endpoint / credentials / facility id "
				"are not set in iHotel Settings → Card Integration."
			)
		return endpoint.rstrip("/"), api_key, facility

	def encode(self, request: EncodeRequest) -> EncodeResult:
		request.validate()
		endpoint, api_key, facility = self._config()
		payload = {
			"facilityId": facility,
			"room": request.room,
			"beginDate": request.valid_from.isoformat(),
			"endDate": request.valid_to.isoformat(),
			"keyType": "duplicate" if request.is_duplicate else "new",
			"accessLevel": request.access_level,
			"commonDoors": request.common_doors,
			"guestName": request.guest_name,
		}
		raise EncoderError(
			"Assa Abloy adapter is scaffolded but not yet verified against this "
			"property's Vostio/Visionline tenant. Confirm the OAuth flow and key "
			"route, then enable it in assa_abloy.py."
		)
		# Reference implementation once verified:
		# import requests
		# resp = requests.post(
		#     f"{endpoint}/v1/facilities/{facility}/keys",
		#     json=payload,
		#     headers={"Authorization": f"Bearer {api_key}"},
		#     timeout=20,
		# )
		# resp.raise_for_status()
		# data = resp.json()
		# return EncodeResult(
		#     card_uid=data["keyId"], vendor=self.vendor,
		#     encoded_at=now_datetime(), raw=data,
		#     mobile_key_token=data.get("mobileKeyUrl"),
		# )

	def cancel(self, card_uid: str) -> None:
		endpoint, api_key, facility = self._config()
		import requests

		resp = requests.delete(
			f"{endpoint}/v1/facilities/{facility}/keys/{card_uid}",
			headers={"Authorization": f"Bearer {api_key}"},
			timeout=20,
		)
		if resp.status_code not in (200, 202, 204, 404):
			raise EncoderError(f"Assa Abloy refused to cancel key {card_uid}: {resp.text}")
