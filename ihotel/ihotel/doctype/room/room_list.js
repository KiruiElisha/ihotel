// Copyright (c) 2026, Noble and contributors
// For license information, please see license.txt

// Colour semantics match the front-desk app (frontend/src/data/status.js):
// green = ready/done, blue = in progress, orange = needs attention,
// red = blocked/problem, grey = inactive.

frappe.listview_settings["Room"] = {
	get_indicator(doc) {
		const colours = {
			"Available": "green",
			"Vacant Clean": "green",
			"Inspected": "green",
			"Occupied": "blue",
			"Occupied Clean": "blue",
			"Dirty": "orange",
			"Vacant Dirty": "orange",
			"Occupied Dirty": "orange",
			"Pickup": "orange",
			"Housekeeping": "orange",
			"Out of Order": "red",
			"Out of Service": "red",
		};
		const value = doc.status;
		return [__(value || "Unknown"), colours[value] || "grey", "status,=," + value];
	},
};
