# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Front-desk API for the card-scanning and key-encoding integrations.

Two capabilities are exposed to the /hotel single-page app:

* **ID / passport scanning** — the browser decodes a document image into raw
  text (passport MRZ or driver-license AAMVA barcode); the server parses it
  into guest fields and optionally writes them onto a Guest.
* **Room key encoding** — issue and cancel electronic room keys through the
  configured lock adapter, logging each one as a Key Card.

Every endpoint requires an authenticated hotel user (see
``frontend_api.require_hotel_user``); nothing here is guest-callable.
"""

from __future__ import annotations

import base64
import json

import frappe
from frappe import _
from frappe.utils import get_datetime, now_datetime

from ihotel.frontend_api import require_hotel_user
from ihotel.integrations.id_scan import parse_document
from ihotel.integrations.key_encoding import EncoderError, get_encoder
from ihotel.integrations.key_encoding.base import EncodeRequest

# UI access-level label -> encoder key.
_ACCESS_KEYS = {
	"Guest": "guest",
	"Suite": "suite",
	"Master": "master",
	"Grand Master": "grand_master",
	"Emergency": "emergency",
}


# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------
@frappe.whitelist()
def get_card_settings() -> dict:
	"""What the app needs to render the scan / encode actions."""
	require_hotel_user()
	s = frappe.get_cached_doc("iHotel Settings")
	return {
		"id_scan": {
			"enabled": bool(getattr(s, "id_scan_enabled", 0)),
			"provider": getattr(s, "id_scan_provider", "Browser Camera"),
			"store_images": bool(getattr(s, "id_scan_store_images", 0)),
		},
		"key_encoding": {
			"enabled": bool(getattr(s, "key_encoding_enabled", 0)),
			"vendor": getattr(s, "key_encoder_vendor", "Mock"),
			"default_access_level": getattr(s, "default_key_access_level", "Guest"),
			"access_levels": list(_ACCESS_KEYS.keys()),
		},
	}


# ----------------------------------------------------------------------
# ID / passport scanning
# ----------------------------------------------------------------------
@frappe.whitelist()
def scan_id(raw_text: str) -> dict:
	"""Parse a decoded MRZ / AAMVA payload into structured guest fields.

	The browser is responsible for turning the document image into ``raw_text``.
	Returns the parsed data plus a ``guest_fields`` dict ready to apply.
	"""
	require_hotel_user()
	if not raw_text or not raw_text.strip():
		frappe.throw(_("No document text to parse."))

	try:
		result = parse_document(raw_text)
	except ValueError as e:
		frappe.throw(str(e))

	data = result.to_dict()
	# Resolve MRZ nationality (ISO alpha-3) to a Country the guest field accepts;
	# unresolved codes are surfaced for display but not auto-applied.
	country = _resolve_country(result.nationality)
	if country:
		data["guest_fields"]["nationality"] = country
	else:
		data["guest_fields"].pop("nationality", None)
	data["nationality_code"] = result.nationality
	return data


@frappe.whitelist()
def apply_id_to_guest(
	data: str | dict,
	guest: str | None = None,
	front_image: str | None = None,
	back_image: str | None = None,
) -> dict:
	"""Write scanned fields onto a Guest, creating one if ``guest`` is omitted.

	``data`` is the payload returned by :func:`scan_id` (its ``guest_fields`` are
	applied). ``front_image`` / ``back_image`` are optional data-URL captures
	stored on the Guest when image storage is enabled. Returns the guest name.
	"""
	require_hotel_user()
	payload = json.loads(data) if isinstance(data, str) else data
	fields = dict(payload.get("guest_fields") or {})
	if not fields:
		frappe.throw(_("Nothing to apply from this scan."))

	if guest:
		doc = frappe.get_doc("Guest", guest)
	else:
		doc = frappe.new_doc("Guest")

	# guest_name / title mapping: Guest uses guest_name; keep title in sync if set.
	for fieldname, value in fields.items():
		if not value:
			continue
		if doc.meta.has_field(fieldname):
			doc.set(fieldname, value)

	doc.save(ignore_permissions=True) if guest else doc.insert(ignore_permissions=True)

	settings = frappe.get_cached_doc("iHotel Settings")
	stored = {}
	if getattr(settings, "id_scan_store_images", 0):
		if front_image:
			stored["id_scan"] = _store_image(doc.name, front_image, "id-front")
		if back_image:
			stored["id_scan_back"] = _store_image(doc.name, back_image, "id-back")
		if stored:
			for fieldname, url in stored.items():
				if doc.meta.has_field(fieldname):
					doc.set(fieldname, url)
			doc.save(ignore_permissions=True)

	return {"guest": doc.name, "guest_name": doc.get("guest_name"), "images": stored}


def _store_image(guest: str, data_url: str, tag: str) -> str:
	"""Persist a base64 data-URL image as a private File on the Guest."""
	content, ext = _decode_data_url(data_url)
	filename = f"{tag}-{frappe.generate_hash(length=6)}.{ext}"
	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": filename,
			"attached_to_doctype": "Guest",
			"attached_to_name": guest,
			"is_private": 1,
			"content": content,
		}
	).insert(ignore_permissions=True)
	return file_doc.file_url


def _decode_data_url(data_url: str) -> tuple[bytes, str]:
	"""Return (bytes, extension) from a ``data:image/png;base64,...`` URL."""
	header, _, b64 = data_url.partition(",")
	if not b64:  # not a data URL — assume raw base64 png
		b64 = header
		ext = "png"
	else:
		mime = header.split(";")[0].removeprefix("data:")
		ext = (mime.split("/")[-1] or "png").replace("jpeg", "jpg")
	return base64.b64decode(b64), ext


def _resolve_country(code: str | None) -> str | None:
	"""Best-effort ISO alpha-3 / alpha-2 code -> Country doctype name.

	Returns None when the code cannot be matched to a Country, so the caller
	can leave nationality for manual selection rather than fail a link check.
	"""
	if not code:
		return None
	code = code.strip().upper()
	alpha2 = _ALPHA3_TO_ALPHA2.get(code, code if len(code) == 2 else None)
	if alpha2:
		name = frappe.db.get_value("Country", {"code": alpha2.lower()}, "name")
		if name:
			return name
	# Some MRZs already carry a name-ish value; try a direct match.
	if frappe.db.exists("Country", code.title()):
		return code.title()
	return None


# A compact map for the codes a property is most likely to see. Unmapped codes
# simply fall through to manual selection.
_ALPHA3_TO_ALPHA2 = {
	"USA": "US", "GBR": "GB", "CAN": "CA", "AUS": "AU", "NZL": "NZ",
	"IND": "IN", "CHN": "CN", "JPN": "JP", "KOR": "KR", "DEU": "DE",
	"FRA": "FR", "ITA": "IT", "ESP": "ES", "NLD": "NL", "CHE": "CH",
	"SWE": "SE", "NOR": "NO", "DNK": "DK", "FIN": "FI", "IRL": "IE",
	"KEN": "KE", "UGA": "UG", "TZA": "TZ", "RWA": "RW", "ETH": "ET",
	"NGA": "NG", "GHA": "GH", "ZAF": "ZA", "EGY": "EG", "MAR": "MA",
	"ARE": "AE", "SAU": "SA", "QAT": "QA", "BRA": "BR", "MEX": "MX",
	"ARG": "AR", "RUS": "RU", "TUR": "TR", "PAK": "PK", "BGD": "BD",
	"SGP": "SG", "MYS": "MY", "IDN": "ID", "THA": "TH", "PHL": "PH",
}


# ----------------------------------------------------------------------
# Room key encoding
# ----------------------------------------------------------------------
@frappe.whitelist()
def encode_key(
	room: str,
	valid_from: str,
	valid_to: str,
	access_level: str = "Guest",
	guest: str | None = None,
	reservation: str | None = None,
	checked_in: str | None = None,
	is_duplicate: int | bool = 0,
	common_doors: str | list | None = None,
) -> dict:
	"""Encode a room key via the configured adapter and log a Key Card."""
	require_hotel_user()
	settings = frappe.get_cached_doc("iHotel Settings")
	if not getattr(settings, "key_encoding_enabled", 0):
		frappe.throw(_("Key encoding is disabled in iHotel Settings."))

	doors = common_doors
	if isinstance(doors, str):
		doors = [d.strip() for d in doors.split(",") if d.strip()] if doors else []

	guest_name = frappe.db.get_value("Guest", guest, "guest_name") if guest else None
	request = EncodeRequest(
		room=room,
		valid_from=get_datetime(valid_from),
		valid_to=get_datetime(valid_to),
		access_level=_ACCESS_KEYS.get(access_level, "guest"),
		guest_name=guest_name,
		reference=reservation or checked_in,
		is_duplicate=bool(int(is_duplicate)) if str(is_duplicate).isdigit() else bool(is_duplicate),
		common_doors=doors or [],
	)

	card = frappe.new_doc("Key Card")
	card.update(
		{
			"guest": guest,
			"room": room,
			"reservation": reservation,
			"checked_in": checked_in,
			"access_level": access_level,
			"valid_from": request.valid_from,
			"valid_to": request.valid_to,
			"is_duplicate": request.is_duplicate,
		}
	)

	try:
		encoder = get_encoder()
		result = encoder.encode(request)
	except EncoderError as e:
		# Persist the failure so there is an audit trail of the attempt.
		card.update({"status": "Failed", "vendor": _current_vendor(settings), "error_message": str(e)})
		card.insert(ignore_permissions=True)
		frappe.db.commit()
		frappe.throw(str(e), title=_("Key Encoding Failed"))

	card.update(
		{
			"status": "Encoded",
			"card_uid": result.card_uid,
			"vendor": result.vendor,
			"mobile_key_token": result.mobile_key_token,
			"encoded_on": result.encoded_at,
			"encoded_by": frappe.session.user,
			"raw_response": frappe.as_json(result.raw) if result.raw else None,
		}
	)
	card.insert(ignore_permissions=True)
	return _card_dict(card)


@frappe.whitelist()
def cancel_key(key_card: str) -> dict:
	"""Invalidate a previously issued key and mark the Key Card cancelled."""
	require_hotel_user()
	card = frappe.get_doc("Key Card", key_card)
	if card.status == "Cancelled":
		return _card_dict(card)
	try:
		encoder = get_encoder(vendor=card.vendor or None)
		if card.card_uid:
			encoder.cancel(card.card_uid)
	except EncoderError as e:
		frappe.throw(str(e), title=_("Key Cancellation Failed"))

	card.mark_cancelled()
	card.save(ignore_permissions=True)
	return _card_dict(card)


@frappe.whitelist()
def list_keys(
	reservation: str | None = None,
	checked_in: str | None = None,
	room: str | None = None,
	guest: str | None = None,
) -> list[dict]:
	"""List Key Cards for a stay / room / guest, newest first."""
	require_hotel_user()
	filters = {}
	if reservation:
		filters["reservation"] = reservation
	if checked_in:
		filters["checked_in"] = checked_in
	if room:
		filters["room"] = room
	if guest:
		filters["guest"] = guest
	if not filters:
		frappe.throw(_("Specify a reservation, check-in, room, or guest."))

	rows = frappe.get_all(
		"Key Card",
		filters=filters,
		fields=[
			"name", "guest", "guest_name", "room", "card_uid", "vendor",
			"access_level", "status", "valid_from", "valid_to", "is_duplicate",
			"encoded_on", "mobile_key_token",
		],
		order_by="creation desc",
	)
	return rows


def _current_vendor(settings) -> str:
	return getattr(settings, "key_encoder_vendor", "Mock") or "Mock"


def _card_dict(card) -> dict:
	return {
		"name": card.name,
		"room": card.room,
		"guest": card.guest,
		"guest_name": card.get("guest_name"),
		"card_uid": card.card_uid,
		"vendor": card.vendor,
		"access_level": card.access_level,
		"status": card.status,
		"valid_from": str(card.valid_from) if card.valid_from else None,
		"valid_to": str(card.valid_to) if card.valid_to else None,
		"is_duplicate": bool(card.is_duplicate),
		"mobile_key_token": card.mobile_key_token,
	}
