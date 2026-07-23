# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Common result type shared by every ID-scan parser."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


# Maps a scan's ``id_type`` to the option stored on the Guest doctype's
# ``id_type`` Select field (Passport / Driver License / National ID / Other).
ID_TYPE_LABELS = {
	"passport": "Passport",
	"driver_license": "Driver License",
	"national_id": "National ID",
	"other": "Other",
}


@dataclass
class ScanResult:
	"""Normalised output of a document scan.

	Every field is optional because different documents expose different data;
	the parser fills what the document actually carries. ``guest_fields`` maps
	directly onto Guest doctype fieldnames so the API can apply it verbatim.
	"""

	id_type: str = "other"  # one of ID_TYPE_LABELS keys
	document_number: str | None = None
	surname: str | None = None
	given_names: str | None = None
	date_of_birth: str | None = None  # ISO yyyy-mm-dd
	expiry_date: str | None = None  # ISO yyyy-mm-dd
	nationality: str | None = None  # ISO 3166 alpha-3 as printed
	issuing_country: str | None = None
	sex: str | None = None  # "Male" | "Female" | "Unspecified"
	address: str | None = None
	# Per-field check-digit results (MRZ only). False means the document text
	# failed its own checksum, so the operator should verify manually.
	checks: dict = field(default_factory=dict)
	# True when every check digit present validated.
	valid: bool = True
	raw: str | None = None

	@property
	def full_name(self) -> str:
		return " ".join(p for p in (self.given_names, self.surname) if p).strip()

	def guest_fields(self) -> dict:
		"""Return a dict keyed by Guest doctype fieldnames, omitting blanks."""
		out = {
			"guest_name": self.full_name or None,
			"id_type": ID_TYPE_LABELS.get(self.id_type, "Other"),
			"id_number": self.document_number,
			"date_of_birth": self.date_of_birth,
			"id_expiry_date": self.expiry_date,
			"gender": self.sex,
			"nationality": self.nationality,
		}
		return {k: v for k, v in out.items() if v}

	def to_dict(self) -> dict:
		d = asdict(self)
		d["full_name"] = self.full_name
		d["guest_fields"] = self.guest_fields()
		return d
