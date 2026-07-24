// Copyright (c) 2026, Noble and contributors
// For license information, please see license.txt

// Guest carries no status field, so the indicator answers the two questions a
// front desk actually asks of a guest list: is this guest restricted, and are
// they a VIP? Restriction wins — it is the one that must not be missed.
frappe.listview_settings["Guest"] = {
	add_fields: ["restricted", "vip_type", "loyalty_tier"],

	get_indicator(doc) {
		if (doc.restricted) {
			return [__("Restricted"), "red", "restricted,=,1"];
		}
		if (doc.vip_type) {
			const vip_colours = {
				"VIP": "purple",
				"VVIP": "purple",
				"Celebrity": "pink",
			};
			return [__(doc.vip_type), vip_colours[doc.vip_type] || "purple", "vip_type,=," + doc.vip_type];
		}
		if (doc.loyalty_tier && doc.loyalty_tier !== "Standard") {
			const tier_colours = {
				"Silver": "grey",
				"Gold": "yellow",
				"Platinum": "blue",
			};
			return [
				__(doc.loyalty_tier),
				tier_colours[doc.loyalty_tier] || "grey",
				"loyalty_tier,=," + doc.loyalty_tier,
			];
		}
		return [__("Guest"), "grey", ""];
	},
};
