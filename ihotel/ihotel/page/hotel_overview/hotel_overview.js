frappe.pages['hotel-overview'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Hotel Overview',
		single_column: true
	});

	// Add modern overview content
	page.main.html(`
		<div class="ho-wrapper">
			<!-- Welcome Section -->
			<div class="ho-welcome-card">
				<div class="ho-welcome-content">
					<h1>Welcome to iHotel Management System</h1>
					<p>Comprehensive hotel management solution for modern hospitality operations</p>
					<div class="ho-welcome-stats">
						<div class="ho-stat-item">
							<div class="ho-stat-number">5+</div>
							<div class="ho-stat-label">Core Modules</div>
						</div>
						<div class="ho-stat-item">
							<div class="ho-stat-number">24/7</div>
							<div class="ho-stat-label">Operations</div>
						</div>
						<div class="ho-stat-item">
							<div class="ho-stat-number">100%</div>
							<div class="ho-stat-label">Integrated</div>
						</div>
					</div>
				</div>
				<div class="ho-welcome-visual">
					<div class="ho-icon-grid">
						<div class="ho-icon-item">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
								<polyline points="9 22 9 12 15 12 15 22"/>
							</svg>
							<span>Rooms</span>
						</div>
						<div class="ho-icon-item">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
								<circle cx="9" cy="7" r="4"/>
								<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
								<path d="M16 3.13a4 4 0 0 1 0 7.75"/>
							</svg>
							<span>Guests</span>
						</div>
						<div class="ho-icon-item">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<rect x="2" y="3" width="20" height="14" rx="2"/>
								<path d="M8 21h8m-4-4v4"/>
							</svg>
							<span>Reports</span>
						</div>
						<div class="ho-icon-item">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
							</svg>
							<span>Billing</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Quick Actions -->
			<div class="ho-quick-actions">
				<h2>Quick Actions</h2>
				<div class="ho-action-grid">
					<a href="/app/room" class="ho-action-card">
						<div class="ho-action-icon rooms">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
								<polyline points="9 22 9 12 15 12 15 22"/>
							</svg>
						</div>
						<div class="ho-action-content">
							<h3>Room Management</h3>
							<p>Manage room inventory, status, and maintenance</p>
						</div>
					</a>
					<a href="/app/guest" class="ho-action-card">
						<div class="ho-action-icon guests">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
								<circle cx="9" cy="7" r="4"/>
							</svg>
						</div>
						<div class="ho-action-content">
							<h3>Guest Profiles</h3>
							<p>View and manage guest information and preferences</p>
						</div>
					</a>
					<a href="/app/reservation" class="ho-action-card">
						<div class="ho-action-icon reservations">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
								<line x1="16" y1="2" x2="16" y2="6"/>
								<line x1="8" y1="2" x2="8" y2="6"/>
								<line x1="3" y1="10" x2="21" y2="10"/>
							</svg>
						</div>
						<div class="ho-action-content">
							<h3>Reservations</h3>
							<p>Handle bookings and reservation management</p>
						</div>
					</a>
					<a href="/app/checked-in" class="ho-action-card">
						<div class="ho-action-icon checkins">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
								<polyline points="10 17 15 12 10 7"/>
								<line x1="15" y1="12" x2="3" y2="12"/>
							</svg>
						</div>
						<div class="ho-action-content">
							<h3>Check-ins</h3>
							<p>Manage guest check-ins and current stays</p>
						</div>
					</a>
				</div>
			</div>

			<!-- System Features -->
			<div class="ho-features">
				<h2>System Features</h2>
				<div class="ho-feature-grid">
					<div class="ho-feature-item">
						<div class="ho-feature-icon">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<circle cx="12" cy="12" r="3"/>
								<path d="M12 1v6m0 6v6m4.22-13.22l4.24 4.24M1.54 1.54l4.24 4.24M20.46 20.46l-4.24-4.24M1.54 20.46l4.24-4.24"/>
							</svg>
						</div>
						<h3>Real-time Updates</h3>
						<p>Live status updates across all modules</p>
					</div>
					<div class="ho-feature-item">
						<div class="ho-feature-icon">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
							</svg>
						</div>
						<h3>Secure Operations</h3>
						<p>Role-based access and data security</p>
					</div>
					<div class="ho-feature-item">
						<div class="ho-feature-icon">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
								<path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
							</svg>
						</div>
						<h3>Comprehensive Reports</h3>
						<p>Detailed analytics and business insights</p>
					</div>
					<div class="ho-feature-item">
						<div class="ho-feature-icon">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<circle cx="12" cy="12" r="10"/>
								<polyline points="12 6 12 12 16 14"/>
							</svg>
						</div>
						<h3>24/7 Availability</h3>
						<p>Round-the-clock system reliability</p>
					</div>
				</div>
			</div>
		</div>
	`);
};