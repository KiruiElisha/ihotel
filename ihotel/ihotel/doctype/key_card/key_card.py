# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime


class KeyCard(Document):
	def validate(self):
		if self.valid_from and self.valid_to:
			if get_datetime(self.valid_to) <= get_datetime(self.valid_from):
				frappe.throw(_("Key expiry must be after its start time."))
		self._sync_expired_status()

	def _sync_expired_status(self):
		# An active/encoded key whose validity window has passed is reported as
		# expired so the board never shows a stale-but-active key.
		if self.status in ("Encoded", "Active") and self.valid_to:
			if get_datetime(self.valid_to) < now_datetime():
				self.status = "Expired"

	def mark_cancelled(self):
		self.status = "Cancelled"
		self.cancelled_on = now_datetime()
