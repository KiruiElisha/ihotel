// Copyright (c) 2026, Noble and contributors
// For license information, please see license.txt

// Colour semantics match the front-desk app (frontend/src/data/status.js):
// green = ready/done, blue = in progress, orange = needs attention,
// red = blocked/problem, grey = inactive.

frappe.listview_settings["Housekeeping Task"] = {
	add_fields: ["priority"],
	get_indicator(doc) {
		const colours = {
			"Pending": "orange",
			"In Progress": "blue",
			"Completed": "green",
		};
		const value = doc.status;
		return [__(value || "Unknown"), colours[value] || "grey", "status,=," + value];
	},

	// Priority reads as a coloured pill alongside the status indicator, so an
	// urgent job is visible without opening the record.
	formatters: {
		priority(value) {
			const colours = {
			"Low": "gray",
			"Normal": "blue",
			"Medium": "blue",
			"High": "orange",
			"Urgent": "red",
			"Critical": "red",
			};
			if (!value) return "";
			return `<span class="indicator-pill ${colours[value] || "gray"}">${__(value)}</span>`;
		},
	},
};
