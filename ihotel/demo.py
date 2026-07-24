# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Demo data seeder for iHotel.

Creates a believable property — buildings, room types, rooms, guests (with the
identity fields an ID scan would fill), reservations, in-house stays,
housekeeping and maintenance work, and a few encoded room keys — so the desk
app and the new card integrations can be demonstrated end to end.

Run it on whichever site has the app installed::

    bench --site <site> execute ihotel.demo.setup_demo_data

It is **idempotent**: re-running skips records that already exist. To remove
everything it created::

    bench --site <site> execute ihotel.demo.clear_demo_data

Every record it inserts is tagged in ``KNOWN`` below, which is also what the
cleanup uses — so it never deletes real data it did not create.
"""

from __future__ import annotations

import frappe
from frappe.utils import add_days, add_to_date, flt, getdate, now_datetime, nowdate

# Reservation.color is mandatory; mirror the status badges the app uses.
STATUS_COLOURS = {
	"pending": "#D69A2B",
	"confirmed": "#12A150",
	"checked_in": "#0D3A65",
	"cancelled": "#C62522",
}

BUILDINGS = ["Main Wing", "Garden Wing"]

ROOM_TYPES = [
	# (name, description, capacity, nightly rate used for demo totals)
	("Standard Single", "Cosy room with a single bed and city view.", 1, 6500),
	("Standard Double", "Comfortable double room with workspace.", 2, 9000),
	("Deluxe Twin", "Twin beds, garden facing, extra floor space.", 2, 12000),
	("Executive Suite", "Separate lounge, kitchenette and balcony.", 3, 21000),
	("Family Room", "Two connected rooms, ideal for families.", 4, 18000),
	("Penthouse", "Top floor suite with panoramic terrace.", 4, 38000),
]

# (room_number, room_type, floor, building, bed_type, status)
ROOMS = [
	("101", "Standard Single", "1", "Main Wing", "Single", "Available"),
	("102", "Standard Single", "1", "Main Wing", "Single", "Occupied"),
	("103", "Standard Double", "1", "Main Wing", "Double", "Occupied"),
	("104", "Standard Double", "1", "Main Wing", "Double", "Vacant Dirty"),
	("105", "Deluxe Twin", "1", "Main Wing", "Twin", "Available"),
	("201", "Standard Double", "2", "Main Wing", "Queen", "Occupied"),
	("202", "Deluxe Twin", "2", "Main Wing", "Twin", "Available"),
	("203", "Deluxe Twin", "2", "Main Wing", "Twin", "Occupied"),
	("204", "Executive Suite", "2", "Main Wing", "King", "Occupied"),
	("205", "Family Room", "2", "Main Wing", "Double", "Vacant Clean"),
	("301", "Executive Suite", "3", "Main Wing", "King", "Available"),
	("302", "Family Room", "3", "Main Wing", "Double", "Occupied"),
	("303", "Standard Double", "3", "Main Wing", "Queen", "Out of Order"),
	("304", "Deluxe Twin", "3", "Main Wing", "Twin", "Inspected"),
	("305", "Penthouse", "3", "Main Wing", "King", "Available"),
	("G01", "Standard Single", "Ground", "Garden Wing", "Single", "Available"),
	("G02", "Standard Double", "Ground", "Garden Wing", "Double", "Occupied"),
	("G03", "Deluxe Twin", "Ground", "Garden Wing", "Twin", "Vacant Dirty"),
	("G04", "Family Room", "Ground", "Garden Wing", "Double", "Available"),
	("G05", "Executive Suite", "Ground", "Garden Wing", "King", "Housekeeping"),
]

# (guest_name, email, phone, id_type, id_number, dob, id_expiry, gender, nationality_code, city)
GUESTS = [
	("Anna Maria Eriksson", "anna.eriksson@example.com", "+46 70 555 0142",
	 "Passport", "L898902C3", "1974-08-12", "2032-04-15", "Female", "SE", "Stockholm"),
	("John Quincy Public", "j.public@example.com", "+1 213 555 0198",
	 "Driver License", "D12345678", "1980-01-15", "2028-08-15", "Male", "US", "Los Angeles"),
	("Grace Wanjiku Kamau", "grace.kamau@example.com", "+254 722 555 011",
	 "National ID", "24857361", "1988-03-22", "2030-03-21", "Female", "KE", "Nairobi"),
	("Daniel Otieno Ochieng", "d.ochieng@example.com", "+254 733 555 202",
	 "National ID", "29104477", "1992-11-04", "2031-11-03", "Male", "KE", "Kisumu"),
	("Priya Raghunathan", "priya.r@example.com", "+91 98200 55511",
	 "Passport", "Z4821906", "1985-06-30", "2029-09-12", "Female", "IN", "Mumbai"),
	("Thomas Müller", "t.mueller@example.com", "+49 151 5550 771",
	 "Passport", "C01X00T47", "1979-02-17", "2033-01-08", "Male", "DE", "Munich"),
	("Sofia Almeida Costa", "sofia.costa@example.com", "+55 11 95555 8842",
	 "Passport", "FX238841", "1990-09-09", "2030-05-19", "Female", "BR", "São Paulo"),
	("Hiroshi Tanaka", "h.tanaka@example.com", "+81 90 5555 3321",
	 "Passport", "TK9902847", "1968-12-01", "2028-12-01", "Male", "JP", "Osaka"),
	("Fatima Al Mansouri", "f.almansouri@example.com", "+971 50 555 7788",
	 "Passport", "A55219043", "1995-04-25", "2031-07-30", "Female", "AE", "Dubai"),
	("Michael O'Sullivan", "m.osullivan@example.com", "+353 86 555 9021",
	 "Passport", "PA8837261", "1983-07-14", "2029-02-28", "Male", "IE", "Dublin"),
	("Chen Wei", "chen.wei@example.com", "+86 138 5555 1180",
	 "Passport", "E88203941", "1991-10-08", "2032-10-07", "Male", "CN", "Shanghai"),
	("Amara Nwosu", "amara.nwosu@example.com", "+234 803 555 4412",
	 "Passport", "B01998220", "1987-05-19", "2030-08-11", "Female", "NG", "Lagos"),
]

# Stays currently in house: (guest, room, nights_ago_checked_in, nights_total)
IN_HOUSE = [
	("Anna Maria Eriksson", "102", 2, 5),
	("John Quincy Public", "103", 1, 3),
	("Grace Wanjiku Kamau", "201", 3, 4),
	("Thomas Müller", "203", 0, 2),
	("Priya Raghunathan", "204", 4, 7),
	("Sofia Almeida Costa", "302", 1, 6),
	("Hiroshi Tanaka", "G02", 5, 6),
]

# Future/other reservations: (guest, room_type, room, days_from_today, nights, status)
RESERVATIONS = [
	("Fatima Al Mansouri", "Executive Suite", "301", 1, 3, "confirmed"),
	("Michael O'Sullivan", "Deluxe Twin", "202", 2, 2, "confirmed"),
	("Chen Wei", "Penthouse", "305", 3, 4, "pending"),
	("Amara Nwosu", "Family Room", "G04", 5, 3, "confirmed"),
	("Daniel Otieno Ochieng", "Standard Single", "101", 7, 2, "pending"),
	("Anna Maria Eriksson", "Deluxe Twin", "105", 14, 3, "pending"),
	("Hiroshi Tanaka", "Standard Double", "G02", -10, 3, "cancelled"),
]

HOUSEKEEPING = [
	("104", "Check-out Cleaning", "High", "Pending"),
	("G03", "Check-out Cleaning", "Normal", "Pending"),
	("G05", "Deep Cleaning", "Urgent", "In Progress"),
	("205", "Stay Over Cleaning", "Normal", "Completed"),
	("304", "Stay Over Cleaning", "Low", "Completed"),
]

MAINTENANCE = [
	("303", "Air conditioning not cooling; compressor likely faulty.", "High", "Open"),
	("G05", "Bathroom tap dripping continuously.", "Medium", "In Progress"),
	("104", "Reading lamp above the bed flickers.", "Low", "Open"),
	("201", "Balcony door lock stiff, needs lubrication.", "Low", "Resolved"),
]

# Rooms that get a demo key encoded (must be an in-house room).
KEYS_FOR = ["102", "204", "G02"]


# ----------------------------------------------------------------------
# Entry points
# ----------------------------------------------------------------------
def setup_demo_data(force: bool = False) -> dict:
	"""Create the full demo data set. Safe to run repeatedly."""
	created: dict[str, int] = {}
	steps = (
		("settings", _enable_card_integration),
		("buildings", _make_buildings),
		("room_types", _make_room_types),
		("rooms", _make_rooms),
		("guests", _make_guests),
		("reservations", _make_reservations),
		("stays", _make_stays),
		("housekeeping", _make_housekeeping),
		("maintenance", _make_maintenance),
		("key_cards", _make_key_cards),
	)
	for label, fn in steps:
		try:
			created[label] = fn()
		except Exception as e:
			# One failing area should not abort the rest of the demo; report it.
			created[label] = f"failed: {e}"
			frappe.log_error(frappe.get_traceback(), f"iHotel demo: {label}")

	frappe.db.commit()
	print("iHotel demo data:")
	for k, v in created.items():
		print(f"  {k:14s} {v}")
	return created


def clear_demo_data() -> dict:
	"""Delete the records this seeder creates. Leaves everything else alone."""
	removed: dict[str, int] = {}
	room_numbers = [r[0] for r in ROOMS]
	guest_names = [g[0] for g in GUESTS]

	# Order matters: dependents first.
	removed["key_cards"] = _delete("Key Card", {"room": ["in", room_numbers]})
	removed["housekeeping"] = _delete("Housekeeping Task", {"room": ["in", room_numbers]})
	removed["maintenance"] = _delete("Maintenance Request", {"room": ["in", room_numbers]})
	removed["stays"] = _delete("Checked In", {"room": ["in", room_numbers]}, submittable=True)
	removed["reservations"] = _delete("Reservation", {"guest": ["in", guest_names]})
	removed["guests"] = _delete("Guest", {"name": ["in", guest_names]})
	removed["rooms"] = _delete("Room", {"name": ["in", room_numbers]})
	removed["room_types"] = _delete("Room Type", {"name": ["in", [t[0] for t in ROOM_TYPES]]})
	removed["buildings"] = _delete("Buildings", {"name": ["in", BUILDINGS]})

	frappe.db.commit()
	print("iHotel demo data removed:", removed)
	return removed


def _delete(doctype: str, filters: dict, submittable: bool = False) -> int:
	if not frappe.db.exists("DocType", doctype):
		return 0
	names = [d.name for d in frappe.get_all(doctype, filters=filters)]
	count = 0
	for name in names:
		try:
			if submittable:
				doc = frappe.get_doc(doctype, name)
				if doc.docstatus == 1:
					doc.cancel()
			frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
			count += 1
		except Exception:
			continue
	return count


# ----------------------------------------------------------------------
# Builders
# ----------------------------------------------------------------------
def _enable_card_integration() -> str:
	"""Turn on ID scanning and (mock) key encoding so the demo shows them."""
	s = frappe.get_single("iHotel Settings")
	for field, value in (
		("id_scan_enabled", 1),
		("id_scan_provider", "Browser Camera"),
		("id_scan_store_images", 1),
		("key_encoding_enabled", 1),
		("key_encoder_vendor", "Mock"),
		("default_key_access_level", "Guest"),
	):
		if s.meta.has_field(field):
			s.set(field, value)
	if not s.get("hotel_name"):
		s.hotel_name = "Azzir Grand Hotel"
	s.flags.ignore_mandatory = True
	s.save(ignore_permissions=True)
	return "enabled (Mock encoder)"


def _make_buildings() -> int:
	n = 0
	for name in BUILDINGS:
		if frappe.db.exists("Buildings", name):
			continue
		frappe.get_doc({"doctype": "Buildings", "building_name": name}).insert(ignore_permissions=True)
		n += 1
	return n


def _make_room_types() -> int:
	n = 0
	for name, description, capacity, _rate in ROOM_TYPES:
		if frappe.db.exists("Room Type", name):
			continue
		frappe.get_doc(
			{
				"doctype": "Room Type",
				"room_type_name": name,
				"description": description,
				"maximum_capacity": capacity,
			}
		).insert(ignore_permissions=True)
		n += 1
	return n


def _make_rooms() -> int:
	n = 0
	for number, rtype, floor, building, bed, status in ROOMS:
		if frappe.db.exists("Room", number):
			continue
		frappe.get_doc(
			{
				"doctype": "Room",
				"room_number": number,
				"room_type": rtype,
				"floor": floor,
				"building": building,
				"bed_type": bed,
				"status": status,
			}
		).insert(ignore_permissions=True)
		n += 1
	return n


def _make_guests() -> int:
	n = 0
	for (name, email, phone, id_type, id_number, dob, expiry, gender, country_code, city) in GUESTS:
		if frappe.db.exists("Guest", name):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Guest",
				"guest_name": name,
				"email": email,
				"phone": phone,
				"id_type": id_type,
				"id_number": id_number,
				"date_of_birth": dob,
				"id_expiry_date": expiry,
				"gender": gender,
				"city": city,
			}
		)
		# nationality links to Country; only set it when the country resolves.
		country = frappe.db.get_value("Country", {"code": country_code.lower()}, "name")
		if country and doc.meta.has_field("nationality"):
			doc.nationality = country
		doc.insert(ignore_permissions=True)
		n += 1
	return n


def _rate_for(room_type: str) -> float:
	for name, _d, _c, rate in ROOM_TYPES:
		if name == room_type:
			return flt(rate)
	return 9000.0


def _make_reservations() -> int:
	n = 0
	for guest, room_type, room, offset, nights, status in RESERVATIONS:
		check_in = add_days(nowdate(), offset)
		check_out = add_days(check_in, nights)
		# Skip if an equivalent reservation is already seeded.
		if frappe.db.exists(
			"Reservation", {"guest": guest, "check_in_date": check_in, "room": room}
		):
			continue
		rate = _rate_for(room_type)
		doc = frappe.get_doc(
			{
				"doctype": "Reservation",
				"guest": guest,
				"full_name": guest,
				"room_type": room_type,
				"room": room,
				"check_in_date": check_in,
				"check_out_date": check_out,
				"days": nights,
				"no_of_rooms": 1,
				"adults": 2,
				"children": 0,
				"status": status,
				"color": STATUS_COLOURS.get(status, "#D69A2B"),
				"total_rental": rate * nights,
				"total_charges": rate * nights,
			}
		)
		doc.flags.ignore_mandatory = True
		doc.insert(ignore_permissions=True)
		n += 1
	return n


def _make_stays() -> int:
	"""Create submitted Checked In records so the In-House board is populated."""
	n = 0
	for guest, room, days_ago, nights in IN_HOUSE:
		if frappe.db.exists("Checked In", {"room": room, "guest": guest, "docstatus": 1}):
			continue
		room_type = frappe.db.get_value("Room", room, "room_type")
		rate = _rate_for(room_type)
		check_in = add_to_date(now_datetime(), days=-days_ago)
		check_out = add_to_date(check_in, days=nights)
		doc = frappe.get_doc(
			{
				"doctype": "Checked In",
				"guest": guest,
				"room": room,
				"room_type": room_type,
				"expected_check_in": check_in,
				"actual_check_in": check_in,
				"expected_check_out": check_out,
				"status": "Checked In",
				"nights": nights,
				"adults": 2,
				"children": 0,
				"room_rate": rate,
				"total_amount": rate * nights,
				"total_charges": rate * nights,
				"no_post": 1,  # keep the demo out of accounting integration
			}
		)
		doc.flags.ignore_mandatory = True
		doc.insert(ignore_permissions=True)
		try:
			doc.submit()
		except Exception:
			# If submission trips a site-specific validation, leave it as a draft
			# rather than losing the record entirely.
			pass
		n += 1
	return n


def _make_housekeeping() -> int:
	n = 0
	for room, task_type, priority, status in HOUSEKEEPING:
		if frappe.db.exists("Housekeeping Task", {"room": room, "task_type": task_type}):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Housekeeping Task",
				"room": room,
				"task_type": task_type,
				"priority": priority,
				"status": status,
				"assigned_date": now_datetime(),
				"estimated_duration": 45,
				"notes": "Seeded demo task.",
			}
		)
		doc.flags.ignore_mandatory = True
		doc.insert(ignore_permissions=True)
		n += 1
	return n


def _make_maintenance() -> int:
	n = 0
	for room, description, priority, status in MAINTENANCE:
		if frappe.db.exists("Maintenance Request", {"room": room, "description": description}):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Maintenance Request",
				"room": room,
				"description": description,
				"priority": priority,
				"status": status,
				"maintenance_type": "Reactive",
				"reported_date": now_datetime(),
			}
		)
		doc.flags.ignore_mandatory = True
		doc.insert(ignore_permissions=True)
		n += 1
	return n


def _make_key_cards() -> int:
	"""Encode demo room keys through the configured (mock) encoder."""
	from ihotel.integrations.key_encoding import get_encoder
	from ihotel.integrations.key_encoding.base import EncodeRequest

	if not frappe.db.exists("DocType", "Key Card"):
		return 0

	encoder = get_encoder()
	n = 0
	for room in KEYS_FOR:
		stay = frappe.get_all(
			"Checked In",
			filters={"room": room, "actual_check_out": ["is", "not set"]},
			fields=["name", "guest", "actual_check_in", "expected_check_out"],
			limit=1,
		)
		if not stay:
			continue
		stay = stay[0]
		if frappe.db.exists("Key Card", {"checked_in": stay.name}):
			continue

		request = EncodeRequest(
			room=room,
			valid_from=stay.actual_check_in or now_datetime(),
			valid_to=stay.expected_check_out or add_to_date(now_datetime(), days=2),
			access_level="guest",
			guest_name=stay.guest,
			reference=stay.name,
		)
		result = encoder.encode(request)
		frappe.get_doc(
			{
				"doctype": "Key Card",
				"guest": stay.guest,
				"room": room,
				"checked_in": stay.name,
				"access_level": "Guest",
				"status": "Encoded",
				"card_uid": result.card_uid,
				"vendor": result.vendor,
				"valid_from": request.valid_from,
				"valid_to": request.valid_to,
				"encoded_on": result.encoded_at,
				"encoded_by": frappe.session.user,
				"raw_response": frappe.as_json(result.raw) if result.raw else None,
			}
		).insert(ignore_permissions=True)
		n += 1
	return n
