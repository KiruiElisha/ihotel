# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Parse ICAO 9303 Machine Readable Zones (MRZ).

Supports the three standard layouts:

* **TD3** — passports: 2 lines × 44 characters.
* **TD2** — official travel documents / some ID cards: 2 lines × 36.
* **TD1** — ID cards: 3 lines × 30.

Each numeric field carries a check digit; we validate them and record the
outcome in :attr:`ScanResult.checks` so the front desk can flag a document
whose printed data is inconsistent (a common sign of a bad OCR read or a
tampered document).
"""

from __future__ import annotations

import re
from datetime import date

from .result import ScanResult

# Character values for the ICAO check-digit algorithm: digits are themselves,
# letters are 10-35, and the filler '<' is zero.
_FILLER = "<"


def _char_value(ch: str) -> int:
	if ch.isdigit():
		return int(ch)
	if "A" <= ch <= "Z":
		return ord(ch) - ord("A") + 10
	if ch == _FILLER:
		return 0
	# Anything else (stray OCR noise) contributes zero but will usually make
	# the surrounding check digit fail, which is the signal we want.
	return 0


def check_digit(data: str) -> int:
	"""ICAO 9303 check digit over ``data`` using the 7-3-1 repeating weights."""
	weights = (7, 3, 1)
	total = sum(_char_value(ch) * weights[i % 3] for i, ch in enumerate(data))
	return total % 10


def _verify(data: str, digit: str) -> bool:
	"""True when ``digit`` is the correct check digit for ``data``.

	A filler check digit ('<') is treated as "not present" and passes, matching
	how many issuers leave optional fields unchecked.
	"""
	if digit in ("", _FILLER):
		return True
	if not digit.isdigit():
		return False
	return check_digit(data) == int(digit)


def _clean_lines(raw: str) -> list[str]:
	lines = [ln.strip().upper().replace(" ", "") for ln in raw.strip().splitlines()]
	return [ln for ln in lines if ln]


def is_mrz(raw: str) -> bool:
	"""Cheap sniff: does ``raw`` look like a 2- or 3-line MRZ block?"""
	lines = _clean_lines(raw)
	if len(lines) not in (2, 3):
		return False
	# MRZ uses only A-Z, 0-9 and '<'. Require the block to be dominated by it
	# and every line to be one of the standard widths.
	widths = {len(ln) for ln in lines}
	if len(lines) == 3 and widths <= {30}:
		return all(re.fullmatch(r"[A-Z0-9<]{30}", ln) for ln in lines)
	if len(lines) == 2 and widths <= {44}:
		return all(re.fullmatch(r"[A-Z0-9<]{44}", ln) for ln in lines)
	if len(lines) == 2 and widths <= {36}:
		return all(re.fullmatch(r"[A-Z0-9<]{36}", ln) for ln in lines)
	return False


def parse_mrz(raw: str, today: date | None = None) -> ScanResult:
	"""Parse an MRZ block into a :class:`ScanResult`.

	``today`` fixes the reference date for the two-digit-year century window
	(injectable for deterministic tests); defaults to the current date.
	"""
	lines = _clean_lines(raw)
	if len(lines) == 3 and all(len(ln) == 30 for ln in lines):
		return _parse_td1(lines, today)
	if len(lines) == 2 and all(len(ln) == 44 for ln in lines):
		return _parse_td3(lines, today)
	if len(lines) == 2 and all(len(ln) == 36 for ln in lines):
		return _parse_td2(lines, today)
	raise ValueError("Text is not a recognised MRZ layout (TD1/TD2/TD3)")


def _names(field: str) -> tuple[str, str]:
	"""Split an MRZ name field ``SURNAME<<GIVEN<NAMES`` into (surname, given)."""
	surname, _, given = field.partition("<<")
	surname = surname.replace(_FILLER, " ").strip()
	given = re.sub(r"\s+", " ", given.replace(_FILLER, " ")).strip()
	return _titlecase(surname), _titlecase(given)


def _titlecase(name: str) -> str:
	return " ".join(w.capitalize() for w in name.split())


def _sex(code: str) -> str:
	return {"M": "Male", "F": "Female"}.get(code, "Unspecified")


def _iso_date(yymmdd: str, *, is_expiry: bool, today: date | None) -> str | None:
	"""Convert a 6-digit ``YYMMDD`` MRZ date to ISO ``yyyy-mm-dd``.

	Expiry dates always resolve to the 2000s. Birth dates use a century window:
	a year that would otherwise be in the future is pushed back to the 1900s.
	"""
	if not re.fullmatch(r"\d{6}", yymmdd):
		return None
	yy, mm, dd = int(yymmdd[0:2]), int(yymmdd[2:4]), int(yymmdd[4:6])
	if not (1 <= mm <= 12 and 1 <= dd <= 31):
		return None
	ref = today or date.today()
	if is_expiry:
		year = 2000 + yy
	else:
		year = 2000 + yy
		if year > ref.year:
			year = 1900 + yy
	try:
		return date(year, mm, dd).isoformat()
	except ValueError:
		return None


def _parse_td3(lines: list[str], today: date | None) -> ScanResult:
	l1, l2 = lines
	surname, given = _names(l1[5:])
	doc_no = l2[0:9].replace(_FILLER, "").strip()
	dob = l2[13:19]
	expiry = l2[21:27]
	checks = {
		"document_number": _verify(l2[0:9], l2[9]),
		"date_of_birth": _verify(dob, l2[19]),
		"expiry_date": _verify(expiry, l2[27]),
	}
	return ScanResult(
		id_type="passport",
		document_number=doc_no,
		surname=surname,
		given_names=given,
		date_of_birth=_iso_date(dob, is_expiry=False, today=today),
		expiry_date=_iso_date(expiry, is_expiry=True, today=today),
		nationality=l2[10:13].replace(_FILLER, "") or None,
		issuing_country=l1[2:5].replace(_FILLER, "") or None,
		sex=_sex(l2[20]),
		checks=checks,
		valid=all(checks.values()),
		raw="\n".join(lines),
	)


def _parse_td2(lines: list[str], today: date | None) -> ScanResult:
	l1, l2 = lines
	surname, given = _names(l1[5:])
	doc_no = l2[0:9].replace(_FILLER, "").strip()
	dob = l2[13:19]
	expiry = l2[21:27]
	checks = {
		"document_number": _verify(l2[0:9], l2[9]),
		"date_of_birth": _verify(dob, l2[19]),
		"expiry_date": _verify(expiry, l2[27]),
	}
	id_type = "passport" if l1[0] == "P" else "national_id"
	return ScanResult(
		id_type=id_type,
		document_number=doc_no,
		surname=surname,
		given_names=given,
		date_of_birth=_iso_date(dob, is_expiry=False, today=today),
		expiry_date=_iso_date(expiry, is_expiry=True, today=today),
		nationality=l2[10:13].replace(_FILLER, "") or None,
		issuing_country=l1[2:5].replace(_FILLER, "") or None,
		sex=_sex(l2[20]),
		checks=checks,
		valid=all(checks.values()),
		raw="\n".join(lines),
	)


def _parse_td1(lines: list[str], today: date | None) -> ScanResult:
	l1, l2, l3 = lines
	doc_no = l1[5:14].replace(_FILLER, "").strip()
	dob = l2[0:6]
	expiry = l2[8:14]
	surname, given = _names(l3)
	checks = {
		"document_number": _verify(l1[5:14], l1[14]),
		"date_of_birth": _verify(dob, l2[6]),
		"expiry_date": _verify(expiry, l2[14]),
	}
	id_type = "passport" if l1[0] == "P" else "national_id"
	return ScanResult(
		id_type=id_type,
		document_number=doc_no,
		surname=surname,
		given_names=given,
		date_of_birth=_iso_date(dob, is_expiry=False, today=today),
		expiry_date=_iso_date(expiry, is_expiry=True, today=today),
		nationality=l2[15:18].replace(_FILLER, "") or None,
		issuing_country=l1[2:5].replace(_FILLER, "") or None,
		sex=_sex(l2[7]),
		checks=checks,
		valid=all(checks.values()),
		raw="\n".join(lines),
	)
