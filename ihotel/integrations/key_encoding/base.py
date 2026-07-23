# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""The vendor-neutral key-encoder contract.

An encoder takes an :class:`EncodeRequest` (which room, valid for how long,
what access level) and returns an :class:`EncodeResult` describing the key that
was written. Adapters translate this to and from their vendor's protocol.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime


class EncoderError(Exception):
	"""Raised when a key cannot be encoded or cancelled.

	The message is surfaced to the front desk, so keep it operator-friendly.
	"""


# Access levels the app understands. Adapters map these onto whatever the lock
# system calls them.
ACCESS_LEVELS = ("guest", "suite", "master", "grand_master", "emergency")


@dataclass
class EncodeRequest:
	"""Everything an adapter needs to write one key."""

	room: str  # room number / lock identifier as the property labels it
	valid_from: datetime
	valid_to: datetime
	access_level: str = "guest"
	guest_name: str | None = None
	reference: str | None = None  # e.g. reservation / folio id, for the audit trail
	# When True the adapter should write an additional key that coexists with
	# any already issued for the room (a second guest key) rather than
	# invalidating prior keys.
	is_duplicate: bool = False
	# Extra doors this key should open (spa, parking, lounge...). Adapter-defined.
	common_doors: list[str] = field(default_factory=list)

	def validate(self) -> None:
		if not self.room:
			raise EncoderError("A room is required to encode a key")
		if self.valid_to <= self.valid_from:
			raise EncoderError("Key expiry must be after its start time")
		if self.access_level not in ACCESS_LEVELS:
			raise EncoderError(f"Unknown access level: {self.access_level}")


@dataclass
class EncodeResult:
	"""The outcome of a successful encode."""

	card_uid: str  # unique id of the physical/mobile credential
	vendor: str
	encoded_at: datetime
	raw: dict = field(default_factory=dict)  # vendor response, for debugging
	# Some vendors return a mobile key token / URL instead of writing a card.
	mobile_key_token: str | None = None


class KeyEncoder(abc.ABC):
	"""Base class every vendor adapter implements.

	``config`` is the resolved settings dict for the property (endpoint,
	credentials, facility id, ...). Adapters read what they need from it.
	"""

	#: Human-readable vendor name; also the value stored on the Key Card record.
	vendor: str = "base"

	def __init__(self, config: dict | None = None):
		self.config = config or {}

	@abc.abstractmethod
	def encode(self, request: EncodeRequest) -> EncodeResult:
		"""Write a key for ``request`` and return its :class:`EncodeResult`."""

	@abc.abstractmethod
	def cancel(self, card_uid: str) -> None:
		"""Invalidate a previously issued key. No-op if already inactive."""

	# Adapters that write physical cards need a connected encoder station; the
	# app can surface this so staff know why encoding is unavailable.
	def health_check(self) -> bool:
		"""Return True if the encoder is reachable/ready. Best effort."""
		return True
