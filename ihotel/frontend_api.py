# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""API for the iHotel front-desk app served at /hotel.

Kept separate from `ihotel.api` (which the old dashboard still uses) so the two
can evolve independently. Every endpoint here requires an authenticated user
with a hotel role; nothing is guest-callable.
"""

import json

import frappe
from frappe import _
from frappe.utils import add_to_date, flt, getdate, nowdate

# Any of these may use the front desk. System Manager is included so an
# administrator can always get in.
HOTEL_ROLES = {
	"System Manager",
	"Administrator",
	"Hotel Manager",
	"Front Desk",
	"Housekeeping",
	"iHotel Manager",
	"iHotel User",
}

Payload = dict | str | None

# Reservation carries the guest's name denormalised alongside the link, so the
# list can be rendered without resolving every link.
# Reservation.color is mandatory; these mirror the status badges in the app.
STATUS_COLOURS = {
	"pending": "#D69A2B",
	"confirmed": "#12A150",
	"checked_in": "#0D3A65",
	"cancelled": "#C62522",
}

# Room.status has twelve values; these groupings drive the board and the KPIs.
DIRTY_STATUSES = {"Dirty", "Vacant Dirty", "Occupied Dirty", "Pickup", "Housekeeping"}
OUT_OF_USE_STATUSES = {"Out of Order", "Out of Service"}

RESERVATION_FIELDS = [
	"name", "guest", "full_name", "room_type", "check_in_date", "check_out_date",
	"days", "status",
]


def can_manage() -> bool:
	return bool(HOTEL_ROLES & set(frappe.get_roles()))


def require_hotel_user():
	if not can_manage():
		frappe.throw(_("Not permitted."), frappe.PermissionError)


# ----------------------------------------------------------------------
# Boot
# ----------------------------------------------------------------------
@frappe.whitelist()
def get_boot() -> dict:
	"""Everything the app needs to decide who the user is."""
	user = (
		frappe.db.get_value(
			"User", frappe.session.user, ["full_name", "user_image", "email"], as_dict=True
		)
		or {}
	)

	hotel_name = None
	if frappe.db.exists("DocType", "iHotel Settings"):
		hotel_name = frappe.db.get_single_value("iHotel Settings", "hotel_name")

	return {
		"user": frappe.session.user,
		"full_name": user.get("full_name"),
		"user_image": user.get("user_image"),
		"email": user.get("email"),
		"can_manage": can_manage(),
		"hotel_name": hotel_name or "iHotel",
	}


# ----------------------------------------------------------------------
# Today
# ----------------------------------------------------------------------
@frappe.whitelist()
def get_today() -> dict:
	"""The front desk's morning view: occupancy, arrivals, departures, activity."""
	require_hotel_user()
	today = getdate()

	rooms = frappe.get_all("Room", fields=["name", "status"])
	total = len(rooms)
	by_status: dict[str, int] = {}
	for room in rooms:
		by_status[room.status or "Unknown"] = by_status.get(room.status or "Unknown", 0) + 1

	occupied = by_status.get("Occupied", 0)

	arrivals = frappe.get_all(
		"Reservation",
		filters={"check_in_date": today, "status": ["!=", "cancelled"]},
		fields=RESERVATION_FIELDS,
		order_by="check_in_time asc",
		limit=25,
	)
	departures = frappe.get_all(
		"Reservation",
		filters={"check_out_date": today, "status": ["!=", "cancelled"]},
		fields=RESERVATION_FIELDS,
		order_by="check_out_time asc",
		limit=25,
	)
	_attach_guest_names(arrivals)
	_attach_guest_names(departures)

	revenue = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(total_amount), 0)
		FROM `tabChecked In`
		WHERE DATE(actual_check_in) = %s AND docstatus = 1
		""",
		today,
	)[0][0]

	in_house = frappe.db.count("Checked In", {"docstatus": 1, "actual_check_out": ["is", "not set"]})

	# Room revenue for the classic hotel ratios. ADR is per occupied room,
	# RevPAR per available room -- the two only agree at 100% occupancy.
	room_revenue = flt(
		frappe.db.sql(
			"""
			SELECT COALESCE(SUM(total_amount), 0)
			FROM `tabChecked In`
			WHERE docstatus = 1 AND actual_check_out IS NULL
			"""
		)[0][0]
	)

	out_of_order = sum(
		count for status, count in by_status.items() if status in OUT_OF_USE_STATUSES
	)
	dirty = sum(count for status, count in by_status.items() if status in DIRTY_STATUSES)

	hk_open = frappe.db.count(
		"Housekeeping Task", {"status": ["not in", ["Completed", "Cancelled"]]}
	)
	hk_done = frappe.db.count("Housekeeping Task", {"status": "Completed"})

	return {
		"rooms": {
			"total": total,
			"occupied": occupied,
			"available": by_status.get("Available", 0),
			"out_of_order": out_of_order,
			"dirty": dirty,
			"by_status": by_status,
			"occupancy_pct": (occupied / total * 100) if total else 0,
		},
		"arrivals": arrivals,
		"departures": departures,
		"in_house": in_house,
		"revenue_today": flt(revenue),
		"adr": (room_revenue / in_house) if in_house else 0,
		"revpar": (room_revenue / total) if total else 0,
		"arrivals_pending": len([a for a in arrivals if a.get("status") != "checked_in"]),
		"housekeeping_open": hk_open,
		"housekeeping_done": hk_done,
		"housekeeping_pct": (hk_done / (hk_done + hk_open) * 100) if (hk_done + hk_open) else 0,
		"maintenance_open": frappe.db.count(
			"Maintenance Request", {"status": ["in", ["Open", "In Progress"]]}
		),
		"activity": get_activity(limit=12),
	}


@frappe.whitelist()
def get_activity(limit: int = 20) -> list[dict]:
	"""Recent check-ins, check-outs and bookings, newest first."""
	require_hotel_user()
	since = add_to_date(getdate(), days=-2)
	activity: list[dict] = []

	stays = frappe.get_all(
		"Checked In",
		filters={"creation": [">=", since], "docstatus": 1},
		fields=["name", "guest", "room", "actual_check_in", "actual_check_out", "creation"],
		order_by="creation desc",
		limit=int(limit),
	)
	bookings = frappe.get_all(
		"Reservation",
		filters={"creation": [">=", since]},
		fields=["name", "guest", "full_name", "room_type", "check_in_date", "creation"],
		order_by="creation desc",
		limit=int(limit),
	)

	# Resolve every link once, rather than once per row.
	guests = _names(
		"Guest", "guest_name", [r.guest for r in stays] + [r.guest for r in bookings]
	)
	rooms = _names("Room", "room_number", [r.room for r in stays])

	for row in stays:
		checked_out = bool(row.actual_check_out)
		activity.append(
			{
				"name": row.name,
				"type": "check_out" if checked_out else "check_in",
				"title": "Check-out" if checked_out else "Check-in",
				"description": "{0} · Room {1}".format(
					guests.get(row.guest) or "—", rooms.get(row.room) or "—"
				),
				"on": row.actual_check_out if checked_out else row.actual_check_in,
			}
		)

	for row in bookings:
		activity.append(
			{
				"name": row.name,
				"type": "reservation",
				"title": "New reservation",
				"description": "{0} · {1}".format(
					row.full_name or guests.get(row.guest) or "—", row.room_type or "—"
				),
				"on": row.creation,
			}
		)

	activity.sort(key=lambda a: a["on"] or "", reverse=True)
	return activity[: int(limit)]


# ----------------------------------------------------------------------
# Rooms
# ----------------------------------------------------------------------
@frappe.whitelist()
def get_room_board() -> dict:
	"""Every room with its status and, when occupied, who is in it.

	The old frontend called `get_room_board_data`, which was never implemented --
	this replaces it.
	"""
	require_hotel_user()
	rooms = frappe.get_all(
		"Room",
		fields=["name", "room_number", "room_type", "floor", "status"],
		order_by="floor asc, room_number asc",
	)

	# One query for every current occupant beats one per room.
	occupants = {}
	for stay in frappe.get_all(
		"Checked In",
		filters={"docstatus": 1, "actual_check_out": ["is", "not set"]},
		fields=["name", "room", "guest", "actual_check_in", "expected_check_out"],
	):
		occupants[stay.room] = stay

	guests = _names("Guest", "guest_name", [s.guest for s in occupants.values()])

	for room in rooms:
		stay = occupants.get(room.name)
		room["guest"] = (guests.get(stay.guest) or stay.guest) if stay else None
		room["stay"] = stay.name if stay else None
		room["checked_in_on"] = stay.actual_check_in if stay else None
		room["due_out"] = stay.get("expected_check_out") if stay else None

	statuses = sorted({r.status for r in rooms if r.status})
	floors = sorted({r.floor for r in rooms if r.floor})

	return {"rooms": rooms, "statuses": statuses, "floors": floors}


@frappe.whitelist()
def set_room_status(room: str, status: str) -> dict:
	"""Move a room between Available / Occupied / Dirty and so on."""
	require_hotel_user()
	options = frappe.get_meta("Room").get_field("status").options or ""
	allowed = [o.strip() for o in options.split("\n") if o.strip()]
	if allowed and status not in allowed:
		frappe.throw(_("{0} is not a valid room status.").format(status))

	frappe.db.set_value("Room", room, "status", status)
	return {"room": room, "status": status}


# ----------------------------------------------------------------------
# Reservations, guests, housekeeping
# ----------------------------------------------------------------------
@frappe.whitelist()
def get_reservations(status: str | None = None, limit: int = 200) -> list[dict]:
	require_hotel_user()
	filters: dict = {}
	if status:
		filters["status"] = status

	rows = frappe.get_all(
		"Reservation",
		filters=filters,
		fields=RESERVATION_FIELDS + ["adults", "children", "total_charges", "room", "creation"],
		order_by="check_in_date desc",
		limit=int(limit),
	)
	_attach_guest_names(rows)
	return rows


@frappe.whitelist()
def get_guests(search: str | None = None, limit: int = 200) -> list[dict]:
	require_hotel_user()
	filters = {}
	if search:
		filters["guest_name"] = ["like", f"%{search}%"]

	return frappe.get_all(
		"Guest",
		filters=filters,
		fields=[
			"name", "guest_name", "email", "phone", "city",
			"address_line_1", "id_type", "id_number", "nationality", "creation",
		],
		order_by="creation desc",
		limit=int(limit),
	)


@frappe.whitelist()
def get_housekeeping(status: str | None = None) -> dict:
	require_hotel_user()
	filters: dict = {}
	if status:
		filters["status"] = status

	tasks = frappe.get_all(
		"Housekeeping Task",
		filters=filters,
		fields=[
			"name", "room", "task_type", "priority", "assigned_to",
			"status", "notes", "creation", "actual_end_time",
		],
		order_by="creation desc",
		limit=300,
	)

	counts = {"open": 0, "in_progress": 0, "completed": 0}
	for task in tasks:
		if task.status == "Completed":
			counts["completed"] += 1
		elif task.status == "In Progress":
			counts["in_progress"] += 1
		else:
			counts["open"] += 1

	return {"tasks": tasks, "counts": counts}


@frappe.whitelist()
def set_task_status(task: str, status: str) -> dict:
	require_hotel_user()
	doc = frappe.get_doc("Housekeeping Task", task)
	doc.status = status
	if status == "Completed" and not doc.get("actual_end_time"):
		doc.actual_end_time = frappe.utils.now_datetime()
	doc.save()
	return {"task": task, "status": status}


@frappe.whitelist()
def save_doc(doctype: str, values: Payload = None, name: str | None = None) -> dict:
	"""Create or update one of the front-desk doctypes.

	Whitelisted by doctype so this cannot be used as a general write endpoint,
	and it honours the user's own permissions rather than bypassing them.
	"""
	require_hotel_user()
	if doctype not in ("Reservation", "Guest", "Housekeeping Task", "Maintenance Request"):
		frappe.throw(_("{0} cannot be edited here.").format(doctype), frappe.PermissionError)

	if isinstance(values, str):
		values = json.loads(values)
	values = values or {}
	values.pop("doctype", None)
	values.pop("name", None)

	if name:
		doc = frappe.get_doc(doctype, name)
		doc.update(values)
	else:
		doc = frappe.get_doc({"doctype": doctype, **values})

	if doctype == "Reservation" and not doc.get("color"):
		# Mandatory on the doctype, and what the desk calendar colours by. Deriving
		# it from status keeps the calendar meaningful without asking the front
		# desk to pick a colour.
		doc.color = STATUS_COLOURS.get(doc.get("status"), STATUS_COLOURS["pending"])

	doc.save()
	return doc.as_dict()


@frappe.whitelist()
def get_in_house() -> dict:
	"""Guests currently in the hotel."""
	require_hotel_user()
	stays = frappe.get_all(
		"Checked In",
		filters={"docstatus": 1, "actual_check_out": ["is", "not set"]},
		fields=[
			"name", "guest", "room", "room_type", "actual_check_in", "expected_check_out",
			"nights", "adults", "children", "total_amount", "status", "payment_status",
		],
		order_by="expected_check_out asc",
		limit=300,
	)
	guests = _names("Guest", "guest_name", [s.guest for s in stays])
	rooms = _names("Room", "room_number", [s.room for s in stays])
	today = getdate()

	for stay in stays:
		stay["guest_name"] = guests.get(stay.guest) or stay.guest or "—"
		stay["room_number"] = rooms.get(stay.room) or stay.room or "—"
		due = stay.expected_check_out
		stay["due_out_today"] = bool(due) and getdate(due) == today
		stay["overdue"] = bool(due) and getdate(due) < today

	return {
		"stays": stays,
		"totals": {
			"in_house": len(stays),
			"due_out": len([s for s in stays if s["due_out_today"]]),
			"overdue": len([s for s in stays if s["overdue"]]),
			"revenue": sum(flt(s.total_amount) for s in stays),
		},
	}


@frappe.whitelist()
def check_out(stay: str) -> dict:
	"""Close a stay and hand the room to housekeeping."""
	require_hotel_user()
	doc = frappe.get_doc("Checked In", stay)
	if doc.actual_check_out:
		frappe.throw(_("This stay is already checked out."))

	doc.actual_check_out = frappe.utils.now_datetime()
	doc.status = "Checked Out"
	doc.save()

	if doc.room:
		# A departed room is dirty until housekeeping says otherwise.
		frappe.db.set_value("Room", doc.room, "status", "Vacant Dirty")

	return {"stay": stay, "room": doc.room}


@frappe.whitelist()
def get_maintenance(status: str | None = None) -> dict:
	require_hotel_user()
	filters: dict = {}
	if status:
		filters["status"] = status

	requests = frappe.get_all(
		"Maintenance Request",
		filters=filters,
		fields=[
			"name", "room", "status", "category", "priority", "maintenance_type",
			"assigned_to", "reported_date", "scheduled_date", "description",
			"estimated_cost", "actual_cost",
		],
		order_by="reported_date desc, creation desc",
		limit=300,
	)
	rooms = _names("Room", "room_number", [r.room for r in requests])
	for row in requests:
		row["room_number"] = rooms.get(row.room) or row.room or "—"

	counts = {"open": 0, "in_progress": 0, "resolved": 0}
	for row in requests:
		if row.status == "In Progress":
			counts["in_progress"] += 1
		elif row.status in ("Resolved", "Closed"):
			counts["resolved"] += 1
		else:
			counts["open"] += 1

	return {"requests": requests, "counts": counts}


@frappe.whitelist()
def get_laundry(status: str | None = None) -> dict:
	require_hotel_user()
	filters: dict = {"docstatus": ["<", 2]}
	if status:
		filters["status"] = status

	orders = frappe.get_all(
		"Laundry Order",
		filters=filters,
		fields=[
			"name", "customer_type", "customer", "contact_person", "room_number",
			"order_date", "expected_delivery", "service_type", "processing_mode",
			"status", "total_amount", "outstanding_amount",
		],
		order_by="order_date desc",
		limit=300,
	)

	return {
		"orders": orders,
		"totals": {
			"orders": len(orders),
			"in_progress": len(
				[o for o in orders if o.status in ("Collected", "Processing", "Quality Check")]
			),
			"ready": len([o for o in orders if o.status == "Ready"]),
			"outstanding": sum(flt(o.outstanding_amount) for o in orders),
		},
	}


@frappe.whitelist()
def get_night_audit() -> dict:
	"""Past audits plus the figures today's audit would record."""
	require_hotel_user()
	audits = frappe.get_all(
		"Night Audit",
		filters={"docstatus": ["<", 2]},
		fields=[
			"name", "audit_date", "performed_by", "total_rooms", "occupied_rooms",
			"occupancy_rate", "adr", "revpar", "total_revenue",
		],
		order_by="audit_date desc",
		limit=60,
	)

	today = get_today()
	return {
		"audits": audits,
		"tonight": {
			"audit_date": nowdate(),
			"total_rooms": today["rooms"]["total"],
			"occupied_rooms": today["rooms"]["occupied"],
			"occupancy_rate": today["rooms"]["occupancy_pct"],
			"adr": today["adr"],
			"revpar": today["revpar"],
			"total_revenue": today["revenue_today"],
		},
		"last_audit": audits[0] if audits else None,
	}


@frappe.whitelist()
def get_lists() -> dict:
	"""Dropdown sources for the front-desk forms."""
	require_hotel_user()

	def options(doctype: str, field: str) -> list[str]:
		meta = frappe.get_meta(doctype)
		f = meta.get_field(field)
		return [o.strip() for o in (f.options or "").split("\n") if o.strip()] if f else []

	return {
		"room_types": frappe.get_all("Room Type", pluck="name", order_by="name"),
		"countries": frappe.get_all("Country", pluck="name", order_by="name", limit=300),
		"guest_id_types": options("Guest", "id_type"),
		"rooms": frappe.get_all(
			"Room", fields=["name", "room_number", "status"], order_by="room_number"
		),
		"guests": frappe.get_all("Guest", fields=["name", "guest_name"], order_by="guest_name"),
		"room_statuses": options("Room", "status"),
		"reservation_statuses": options("Reservation", "status"),
		"task_statuses": options("Housekeeping Task", "status"),
		"task_types": options("Housekeeping Task", "task_type"),
		"priorities": options("Housekeeping Task", "priority"),
		"maintenance_statuses": options("Maintenance Request", "status"),
		"maintenance_priorities": options("Maintenance Request", "priority"),
		"maintenance_types": options("Maintenance Request", "maintenance_type"),
		"maintenance_categories": frappe.get_all(
			"Maintenance Category", pluck="name", order_by="name"
		),
		"laundry_statuses": options("Laundry Order", "status"),
		"today": nowdate(),
	}


# ----------------------------------------------------------------------
def _names(doctype: str, field: str, ids) -> dict[str, str]:
	"""Resolve a set of link values to display names in a single query."""
	ids = {i for i in ids if i}
	if not ids:
		return {}
	return dict(
		frappe.get_all(
			doctype, filters={"name": ["in", list(ids)]}, as_list=True, fields=["name", field]
		)
	)


def _attach_guest_names(rows: list) -> None:
	"""Resolve guest links to names in one query rather than one per row."""
	ids = {r.guest for r in rows if r.get("guest")}
	names = (
		dict(
			frappe.get_all(
				"Guest",
				filters={"name": ["in", list(ids)]},
				as_list=True,
				fields=["name", "guest_name"],
			)
		)
		if ids
		else {}
	)
	for row in rows:
		row["guest_name"] = (
			row.get("full_name") or names.get(row.get("guest")) or row.get("guest") or "—"
		)
