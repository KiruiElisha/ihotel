# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Expose the iHotel script reports to the front-desk app.

The app ships ten script reports that were previously only reachable from the
desk. This module publishes a catalogue of them — including a description of
each report's filters — so the SPA can render filter controls generically, and
runs them through Frappe's query-report engine (which applies the report's own
permissions).
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import add_days, nowdate

from ihotel.frontend_api import require_hotel_user

# Filter descriptors understood by the front end:
#   type: "date" | "select" | "link" | "number"
#   default: "today" | "month_start" | literal | None
_TODAY = {"type": "date", "default": "today"}
_FROM = {"fieldname": "from_date", "label": "From", "type": "date", "default": "month_start"}
_TO = {"fieldname": "to_date", "label": "To", "type": "date", "default": "today"}


def _link(fieldname, label, doctype):
	return {"fieldname": fieldname, "label": label, "type": "link", "doctype": doctype}


def _select(fieldname, label, options):
	return {"fieldname": fieldname, "label": label, "type": "select", "options": options}


def _date(fieldname, label, default=None):
	return {"fieldname": fieldname, "label": label, "type": "date", "default": default}


# The catalogue. `category` drives the tabs in the app.
REPORTS = [
	{
		"name": "Occupancy Report",
		"category": "Front Office",
		"icon": "bed-double",
		"description": "Nightly occupancy, ADR and RevPAR across a date range.",
		"filters": [_FROM, _TO],
	},
	{
		"name": "Arrivals And Departures",
		"category": "Front Office",
		"icon": "plane-takeoff",
		"description": "Who is arriving and departing on a given day.",
		"filters": [_date("date", "Date", "today")],
	},
	{
		"name": "Guest History",
		"category": "Front Office",
		"icon": "user-round-search",
		"description": "Every past stay for a guest, with nights and spend.",
		"filters": [_link("guest", "Guest", "Guest")],
	},
	{
		"name": "Revenue Report",
		"category": "Revenue",
		"icon": "trending-up",
		"description": "Room revenue by period, room type and business source.",
		"filters": [
			_FROM,
			_TO,
			_link("room_type", "Room Type", "Room Type"),
			_link("business_source", "Business Source", "Business Source Category"),
		],
	},
	{
		"name": "Daily Tax Report",
		"category": "Revenue",
		"icon": "receipt",
		"description": "Tax collected for a day, broken down by rate and room type.",
		"filters": [
			_date("date", "Date", "today"),
			_link("rate_type", "Rate Type", "Rate Type"),
			_link("room_type", "Room Type", "Room Type"),
		],
	},
	{
		"name": "Outstanding Balance",
		"category": "Revenue",
		"icon": "wallet",
		"description": "Folios still carrying a balance.",
		"filters": [
			_link("guest", "Guest", "Guest"),
			{"fieldname": "min_amount", "label": "Minimum amount", "type": "number"},
		],
	},
	{
		"name": "Housekeeping Status",
		"category": "Operations",
		"icon": "sparkles",
		"description": "Cleaning workload and completion by attendant.",
		"filters": [
			_FROM,
			_TO,
			_select("status", "Status", ["Pending", "In Progress", "Completed"]),
			_link("assigned_to", "Assigned to", "User"),
		],
	},
	{
		"name": "Maintenance Report",
		"category": "Operations",
		"icon": "wrench",
		"description": "Open and resolved maintenance work by room and priority.",
		"filters": [
			_link("room", "Room", "Room"),
			_link("category", "Category", "Maintenance Category"),
			_select("maintenance_type", "Type", ["Reactive", "Preventive"]),
			_select("priority", "Priority", ["Low", "Medium", "High", "Critical"]),
			_select("status", "Status", ["Open", "In Progress", "Resolved", "Closed"]),
		],
	},
	{
		"name": "Laundry Profitability",
		"category": "Operations",
		"icon": "shirt",
		"description": "Laundry revenue against cost, by customer and mode.",
		"filters": [
			_FROM,
			_TO,
			_link("customer", "Customer", "Customer"),
			_select("processing_mode", "Processing", ["In-house", "Outsourced"]),
			_select("status", "Status", ["Draft", "In Progress", "Completed", "Delivered"]),
		],
	},
	{
		"name": "Supplier Performance",
		"category": "Operations",
		"icon": "truck",
		"description": "Turnaround and volume by laundry supplier.",
		"filters": [_FROM, _TO, _link("supplier", "Supplier", "Laundry Supplier")],
	},
]

CATEGORIES = ["Front Office", "Revenue", "Operations"]


def _resolve_default(default):
	if default == "today":
		return nowdate()
	if default == "month_start":
		return nowdate()[:8] + "01"
	return default


@frappe.whitelist()
def get_reports() -> dict:
	"""The report catalogue, with defaults resolved and unavailable ones hidden."""
	require_hotel_user()
	available = []
	for spec in REPORTS:
		if not frappe.db.exists("Report", spec["name"]):
			# The report was removed or never installed on this site; don't
			# advertise something that cannot run.
			continue
		item = json.loads(json.dumps(spec))  # deep copy; we mutate defaults
		for f in item["filters"]:
			f.setdefault("label", f["fieldname"].replace("_", " ").title())
			if "default" in f:
				f["default"] = _resolve_default(f["default"])
		available.append(item)

	return {
		"categories": [c for c in CATEGORIES if any(r["category"] == c for r in available)],
		"reports": available,
	}


@frappe.whitelist()
def run_report(report_name: str, filters: str | dict | None = None) -> dict:
	"""Run a script report and return its columns and rows.

	Delegates to Frappe's query-report engine so the report's own permissions
	and formatting metadata apply.
	"""
	require_hotel_user()
	if not any(r["name"] == report_name for r in REPORTS):
		frappe.throw(_("Unknown report: {0}").format(report_name))
	if not frappe.db.exists("Report", report_name):
		frappe.throw(_("Report {0} is not installed on this site.").format(report_name))

	parsed = json.loads(filters) if isinstance(filters, str) else (filters or {})
	# Drop blanks so a report's own defaults apply instead of an empty string.
	parsed = {k: v for k, v in parsed.items() if v not in (None, "", [])}

	from frappe.desk.query_report import run as run_query_report

	result = run_query_report(report_name=report_name, filters=parsed, ignore_prepared_report=True)

	columns = []
	for col in result.get("columns") or []:
		if isinstance(col, str):
			# Legacy "Label:Fieldtype:width" column spec.
			parts = col.split(":")
			columns.append(
				{
					"fieldname": frappe.scrub(parts[0]),
					"label": parts[0],
					"fieldtype": parts[1] if len(parts) > 1 else "Data",
				}
			)
		else:
			columns.append(
				{
					"fieldname": col.get("fieldname"),
					"label": col.get("label"),
					"fieldtype": col.get("fieldtype", "Data"),
					"width": col.get("width"),
				}
			)

	# Normalise rows to dicts keyed by fieldname (script reports may return lists).
	rows = []
	for row in result.get("result") or []:
		if isinstance(row, dict):
			rows.append(row)
		elif isinstance(row, (list, tuple)):
			rows.append({c["fieldname"]: v for c, v in zip(columns, row)})

	return {
		"report": report_name,
		"columns": columns,
		"rows": rows,
		"message": result.get("message"),
	}


@frappe.whitelist()
def get_filter_options(doctype: str, search: str = "", limit: int = 20) -> list[dict]:
	"""Options for a report's link filter, respecting read permission."""
	require_hotel_user()
	if not frappe.has_permission(doctype, "read"):
		frappe.throw(_("Not permitted to read {0}").format(doctype))

	filters = {}
	if search:
		filters["name"] = ["like", f"%{search}%"]
	names = frappe.get_all(doctype, filters=filters, pluck="name", limit=limit, order_by="modified desc")
	return [{"label": n, "value": n} for n in names]
