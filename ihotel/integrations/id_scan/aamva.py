# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Parse the AAMVA barcode on the back of US/Canadian driver licenses.

The PDF417 barcode encodes an AAMVA DL/ID record: a header beginning with
``@`` and ``ANSI ``, followed by newline-separated data elements whose first
three characters are the element id (``DCS`` family name, ``DAC`` first name,
``DAQ`` license number, ``DBB`` date of birth, ``DBA`` expiry, ...).

The browser decodes the barcode image into this raw string; here we turn it
into a :class:`ScanResult`.
"""

from __future__ import annotations

import re
from datetime import date

from .result import ScanResult

_ELEMENT_RE = re.compile(r"^([A-Z]{3})(.*)$")


def is_aamva(raw: str) -> bool:
	"""True when ``raw`` looks like an AAMVA DL/ID barcode payload."""
	head = (raw or "")[:32]
	return "ANSI " in head or head.startswith("@")


def _elements(raw: str) -> dict[str, str]:
	"""Extract the three-letter-keyed data elements from the payload.

	AAMVA separates data elements with LF. Each subfile's first element is
	prefixed by a two-character subfile designator (``DL`` or ``ID``); we strip
	that so the element id underneath is read. The compliance line (``@``) and
	the ``ANSI`` header line carry no guest data and are skipped.
	"""
	# Normalise the record separators AAMVA uses (LF, CR, and the ASCII
	# segment terminators) to plain newlines, then split.
	text = raw.replace("\r", "\n").replace("\x1e", "\n").replace("\x1d", "\n")
	out: dict[str, str] = {}
	for line in text.split("\n"):
		line = line.strip()
		if not line or line.startswith("@"):
			continue
		if line.startswith("ANSI") or line.startswith("AAMVA"):
			continue
		# Drop a leading "DL"/"ID" subfile designator when it precedes a real
		# element id (no AAMVA element id starts with "DL" or "ID", so this is
		# unambiguous).
		if line[:2] in ("DL", "ID") and _ELEMENT_RE.match(line[2:5]):
			line = line[2:]
		m = _ELEMENT_RE.match(line)
		if not m:
			continue
		key, value = m.group(1), m.group(2)
		# Keep the first occurrence of each element id.
		if key not in out:
			out[key] = value.strip()
	return out


def _sex(code: str) -> str:
	# AAMVA encodes sex numerically: 1 male, 2 female, 9 not specified.
	return {"1": "Male", "2": "Female"}.get(code.strip(), "Unspecified")


def _iso_date(value: str, country: str) -> str | None:
	"""Convert an 8-digit AAMVA date to ISO, honouring national field order.

	US records use ``MMDDCCYY``; Canadian records use ``CCYYMMDD``. When the
	country is unknown we try US order first, then fall back to the other.
	"""
	digits = re.sub(r"\D", "", value)
	if len(digits) != 8:
		return None

	def mmddccyy(s):
		return s[4:8], s[0:2], s[2:4]

	def ccyymmdd(s):
		return s[0:4], s[4:6], s[6:8]

	orders = [ccyymmdd, mmddccyy] if country == "CAN" else [mmddccyy, ccyymmdd]
	for order in orders:
		y, m, d = order(digits)
		try:
			return date(int(y), int(m), int(d)).isoformat()
		except ValueError:
			continue
	return None


def _titlecase(name: str) -> str:
	return " ".join(w.capitalize() for w in re.split(r"[\s,]+", name.strip()) if w)


def parse_aamva(raw: str) -> ScanResult:
	"""Parse an AAMVA DL/ID barcode payload into a :class:`ScanResult`."""
	el = _elements(raw)
	if not el:
		raise ValueError("No AAMVA data elements found in barcode")

	country = (el.get("DCG") or "USA").strip().upper()

	surname = el.get("DCS") or el.get("DAB") or ""
	first = el.get("DAC") or el.get("DCT") or ""
	middle = el.get("DAD") or ""
	given = " ".join(p for p in (first, middle) if p and p not in ("NONE", "unavl"))

	address_parts = [
		el.get("DAG"),  # street
		el.get("DAI"),  # city
		el.get("DAJ"),  # state / jurisdiction
		el.get("DAK"),  # postal code
	]
	address = ", ".join(p.strip() for p in address_parts if p and p.strip()) or None

	return ScanResult(
		id_type="driver_license",
		document_number=(el.get("DAQ") or "").strip() or None,
		surname=_titlecase(surname) or None,
		given_names=_titlecase(given) or None,
		date_of_birth=_iso_date(el.get("DBB", ""), country),
		expiry_date=_iso_date(el.get("DBA", ""), country),
		nationality=country or None,
		issuing_country=country or None,
		sex=_sex(el.get("DBC", "")),
		address=address,
		valid=True,  # AAMVA carries no field-level check digits
		raw=raw,
	)
