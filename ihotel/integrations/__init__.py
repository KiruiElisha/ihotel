# Copyright (c) 2026, Noble and contributors
# For license information, please see license.txt

"""Hardware / third-party integrations for iHotel.

Two families live here:

* ``id_scan`` — parse machine-readable travel documents (passport MRZ,
  driver-license AAMVA PDF417) into structured guest fields. The browser
  decodes the image into raw text; the server parses that text so the logic
  is testable and the PII stays server-side.
* ``key_encoding`` — issue electronic room keys through a pluggable encoder.
  A working mock adapter ships today; real lock vendors (Salto, Assa Abloy,
  Onity) are wired through the same interface.
"""
