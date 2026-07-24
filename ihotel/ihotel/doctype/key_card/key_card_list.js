// Copyright (c) 2026, Noble and contributors
// For license information, please see license.txt

// Colour semantics match the front-desk app (frontend/src/data/status.js):
// green = ready/done, blue = in progress, orange = needs attention,
// red = blocked/problem, grey = inactive.

frappe.listview_settings["Key Card"] = {
	get_indicator(doc) {
		const colours = {
			"Encoded": "green",
			"Active": "green",
			"Cancelled": "grey",
			"Expired": "orange",
			"Failed": "red",
		};
		const value = doc.status;
		return [__(value || "Unknown"), colours[value] || "grey", "status,=," + value];
	},
};
