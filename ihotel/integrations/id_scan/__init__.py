# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Parse machine-readable identity documents into structured guest fields.

The browser captures the document image and decodes it into raw text — the
passport Machine Readable Zone (MRZ) or the AAMVA barcode string on the back
of a driver license. That raw text is posted to the server, and these parsers
turn it into the fields the Guest doctype expects.

Public entry point: :func:`parse_document`, which sniffs the format and
dispatches to the MRZ or AAMVA parser.
"""

from __future__ import annotations

from .aamva import is_aamva, parse_aamva
from .mrz import is_mrz, parse_mrz
from .result import ScanResult


def parse_document(raw_text: str) -> ScanResult:
	"""Detect the document format from ``raw_text`` and parse it.

	Raises ``ValueError`` if the text matches neither a known MRZ layout nor
	an AAMVA barcode.
	"""
	text = (raw_text or "").strip()
	if not text:
		raise ValueError("No document text supplied")

	if is_aamva(text):
		return parse_aamva(text)
	if is_mrz(text):
		return parse_mrz(text)

	raise ValueError(
		"Unrecognised document. Expected a passport/ID MRZ or a driver-license "
		"barcode (AAMVA PDF417)."
	)


__all__ = [
	"ScanResult",
	"parse_document",
	"parse_mrz",
	"parse_aamva",
	"is_mrz",
	"is_aamva",
]
