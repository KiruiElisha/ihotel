<template>
  <div class="frappe-app-page">
    <div class="frappe-container">
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-title">Guests</div>
        <div class="page-actions">
          <Button 
            icon="plus" 
            @click="showNewGuestModal = true"
            class="btn-primary"
          >
            Add Guest
          </Button>
        </div>
      </div>

      <!-- Filters -->
      <div class="card">
        <div class="card-body">
          <div class="row">
            <div class="col-md-4">
              <label class="control-label">Search</label>
              <div class="input-group">
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search guest name, email, or phone..."
                  class="form-control"
                >
                <div class="input-group-addon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                  </svg>
                </div>
              </div>
            </div>
            
            <div class="col-md-3">
              <label class="control-label">Guest Type</label>
              <select v-model="selectedGuestType" class="form-control">
                <option value="">All Guest Types</option>
                <option value="Individual">Individual</option>
                <option value="Corporate">Corporate</option>
                <option value="Group">Group</option>
                <option value="VIP">VIP</option>
              </select>
            </div>
            
            <div class="col-md-3">
              <label class="control-label">Nationality</label>
              <select v-model="selectedNationality" class="form-control">
                <option value="">All Nationalities</option>
                <option v-for="nationality in nationalities" :key="nationality" :value="nationality">{{ nationality }}</option>
              </select>
            </div>
            
            <div class="col-md-2">
              <label class="control-label">&nbsp;</label>
              <div>
                <Button @click="clearFilters" icon="x">Clear Filters</Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Guest Cards Grid -->
      <div class="guest-grid">
        <div v-if="$resources.guests.loading" class="text-center py-8">
          <LoadingText />
        </div>
        <div v-else-if="filteredGuests.length === 0" class="text-muted text-center py-8">
          No guests match the current filters
        </div>
        <div v-else class="row">
          <div 
            v-for="guest in filteredGuests" 
            :key="guest.name"
            class="col-md-4 col-lg-3"
          >
            <div class="guest-card" @click="selectGuest(guest)">
              <div class="guest-avatar">
                <div class="avatar avatar-lg bg-primary">
                  <span class="avatar-text">{{ getGuestInitials(guest) }}</span>
                </div>
                <div class="guest-status" :class="getGuestStatusClass(guest)">
                  {{ getGuestStatus(guest) }}
                </div>
              </div>
              
              <div class="guest-info">
                <h4 class="guest-name">{{ guest.guest_name }}</h4>
                <div class="guest-details">
                  <div class="detail-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                    <span>{{ guest.email || 'No email' }}</span>
                  </div>
                  <div class="detail-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/>
                    </svg>
                    <span>{{ guest.phone || 'No phone' }}</span>
                  </div>
                  <div class="detail-item" v-if="guest.nationality">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M3 21v-4a4 4 0 014-4h5a4 4 0 014 4v4M3 21h18M17 16a4 4 0 00-4 4v4M17 16l-4 4m4-4l4 4"/>
                    </svg>
                    <span>{{ guest.nationality }}</span>
                  </div>
                </div>
              </div>
              
              <div class="guest-actions">
                <Button 
                  @click.stop="viewGuest(guest)" 
                  class="btn-default btn-sm"
                  icon="eye"
                >
                  View
                </Button>
                <Button 
                  @click.stop="editGuest(guest)" 
                  class="btn-primary btn-sm"
                  icon="edit"
                >
                  Edit
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Guest Details Modal -->
      <Dialog v-model="showGuestDetails" :title="`Guest: ${selectedGuest?.guest_name}`" size="large">
        <div v-if="selectedGuest" class="guest-details">
          <div class="row">
            <div class="col-md-4">
              <div class="text-center">
                <div class="avatar avatar-xl bg-primary mb-3">
                  <span class="avatar-text">{{ getGuestInitials(selectedGuest) }}</span>
                </div>
                <div :class="['badge mb-3', getGuestStatusClass(selectedGuest)]">
                  {{ getGuestStatus(selectedGuest) }}
                </div>
              </div>
            </div>
            
            <div class="col-md-8">
              <div class="detail-section">
                <h4>Personal Information</h4>
                <div class="detail-list">
                  <div class="detail-item">
                    <span class="detail-label">Full Name:</span>
                    <span class="detail-value">{{ selectedGuest.guest_name }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Email:</span>
                    <span class="detail-value">{{ selectedGuest.email || 'Not provided' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Phone:</span>
                    <span class="detail-value">{{ selectedGuest.phone || 'Not provided' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Address:</span>
                    <span class="detail-value">{{ selectedGuest.address || 'Not provided' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Nationality:</span>
                    <span class="detail-value">{{ selectedGuest.nationality || 'Not provided' }}</span>
                  </div>
                  <div class="detail-item" v-if="selectedGuest.id_type">
                    <span class="detail-label">ID Type:</span>
                    <span class="detail-value">{{ selectedGuest.id_type }}</span>
                  </div>
                  <div class="detail-item" v-if="selectedGuest.id_number">
                    <span class="detail-label">ID Number:</span>
                    <span class="detail-value">{{ selectedGuest.id_number }}</span>
                  </div>
                </div>
              </div>
              
              <div class="detail-section">
                <h4>Booking History</h4>
                <div class="booking-history">
                  <div v-if="guestBookings.length === 0" class="text-muted">
                    No booking history available
                  </div>
                  <div v-else class="booking-list">
                    <div v-for="booking in guestBookings" :key="booking.name" class="booking-item">
                      <div class="booking-info">
                        <div class="booking-title">{{ booking.name }}</div>
                        <div class="booking-dates">
                          {{ formatDate(booking.arrival_date) }} - {{ formatDate(booking.departure_date) }}
                        </div>
                        <div class="booking-status">
                          <span :class="['badge', getStatusClass(booking.status)]">{{ booking.status }}</span>
                        </div>
                      </div>
                      <div class="booking-amount">{{ formatCurrency(booking.total_amount) }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <template #actions>
          <Button 
            @click="editGuest(selectedGuest)"
            class="btn-primary"
            icon="edit"
          >
            Edit Guest
          </Button>
          <Button 
            @click="createReservation(selectedGuest)"
            class="btn-success"
            icon="plus"
          >
            New Reservation
          </Button>
        </template>
      </Dialog>

      <!-- New Guest Modal -->
      <Dialog v-model="showNewGuestModal" title="Add New Guest" size="large">
        <form @submit.prevent="createGuest" class="guest-form">
          <div class="row">
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Guest Name *</label>
                <input 
                  v-model="newGuest.guest_name" 
                  type="text" 
                  required
                  class="form-control"
                  placeholder="Enter full name"
                >
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Email</label>
                <input 
                  v-model="newGuest.email" 
                  type="email" 
                  class="form-control"
                  placeholder="Enter email address"
                >
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Phone</label>
                <input 
                  v-model="newGuest.phone" 
                  type="tel" 
                  class="form-control"
                  placeholder="Enter phone number"
                >
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Nationality</label>
                <input 
                  v-model="newGuest.nationality" 
                  type="text" 
                  class="form-control"
                  placeholder="Enter nationality"
                >
              </div>
            </div>
            
            <div class="col-md-12">
              <div class="form-group">
                <label class="control-label">Address</label>
                <textarea 
                  v-model="newGuest.address" 
                  rows="3"
                  class="form-control"
                  placeholder="Enter address"
                ></textarea>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">ID Type</label>
                <select v-model="newGuest.id_type" class="form-control">
                  <option value="">Select ID Type</option>
                  <option value="Passport">Passport</option>
                  <option value="Driver License">Driver License</option>
                  <option value="National ID">National ID</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">ID Number</label>
                <input 
                  v-model="newGuest.id_number" 
                  type="text" 
                  class="form-control"
                  placeholder="Enter ID number"
                >
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <Button type="button" @click="showNewGuestModal = false" class="btn-default">
              Cancel
            </Button>
            <Button type="submit" class="btn-primary" :loading="creatingGuest">
              Add Guest
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  </div>
</template>

<script>
import { Button, Dialog, LoadingText } from 'frappe-ui'

export default {
  name: 'Guests',
  components: {
    Button,
    Dialog,
    LoadingText
  },
  data() {
    return {
      searchQuery: '',
      selectedGuestType: '',
      selectedNationality: '',
      showNewGuestModal: false,
      showGuestDetails: false,
      selectedGuest: null,
      creatingGuest: false,
      newGuest: {
        guest_name: '',
        email: '',
        phone: '',
        address: '',
        nationality: '',
        id_type: '',
        id_number: ''
      },
      guestBookings: []
    }
  },
  resources: {
    guests: {
      url: 'ihotel.api.get_guests',
      auto: true
    },
    create_guest: {
      method: 'POST',
      url: 'ihotel.api.create_guest'
    }
  },
  computed: {
    guests() {
      return this.$resources.guests.data || []
    },
    filteredGuests() {
      return this.guests.filter(guest => {
        const matchesSearch = !this.searchQuery || 
          guest.guest_name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          (guest.email && guest.email.toLowerCase().includes(this.searchQuery.toLowerCase())) ||
          (guest.phone && guest.phone.toLowerCase().includes(this.searchQuery.toLowerCase()))
        
        const matchesType = !this.selectedGuestType || guest.guest_type === this.selectedGuestType
        const matchesNationality = !this.selectedNationality || guest.nationality === this.selectedNationality
        
        return matchesSearch && matchesType && matchesNationality
      })
    },
    nationalities() {
      const nationalities = [...new Set(this.guests.map(g => g.nationality).filter(Boolean))]
      return nationalities.sort()
    }
  },
  methods: {
    getGuestInitials(guest) {
      return guest.guest_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    },
    
    getGuestStatus(guest) {
      // Mock status based on recent activity
      const hasRecentBookings = this.hasRecentBookings(guest)
      return hasRecentBookings ? 'Active' : 'Inactive'
    },
    
    getGuestStatusClass(guest) {
      const status = this.getGuestStatus(guest)
      return status === 'Active' ? 'badge-success' : 'badge-secondary'
    },
    
    hasRecentBookings(guest) {
      // Mock logic - in real app would check actual booking dates
      return Math.random() > 0.5
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount || 0)
    },
    
    getStatusClass(status) {
      const statusClasses = {
        'Confirmed': 'badge-success',
        'Pending': 'badge-warning',
        'Cancelled': 'badge-danger',
        'Checked In': 'badge-primary',
        'Checked Out': 'badge-secondary',
      }
      return statusClasses[status] || 'badge-secondary'
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.selectedGuestType = ''
      this.selectedNationality = ''
    },
    
    selectGuest(guest) {
      this.selectedGuest = guest
      this.showGuestDetails = true
      this.loadGuestBookings(guest)
    },
    
    viewGuest(guest) {
      this.selectedGuest = guest
      this.showGuestDetails = true
      this.loadGuestBookings(guest)
    },
    
    editGuest(guest) {
      this.selectedGuest = guest
      // In a real app, would open edit modal
      alert(`Edit guest: ${guest.guest_name}`)
    },
    
    createReservation(guest) {
      this.showGuestDetails = false
      alert(`Create reservation for guest ${guest.guest_name}`)
    },
    
    loadGuestBookings(guest) {
      // Mock booking data - in real app would fetch from backend
      this.guestBookings = [
        {
          name: 'RES-001',
          arrival_date: '2024-01-25',
          departure_date: '2024-01-28',
          status: 'Confirmed',
          total_amount: 750
        },
        {
          name: 'RES-002',
          arrival_date: '2023-12-15',
          departure_date: '2023-12-18',
          status: 'Checked Out',
          total_amount: 450
        }
      ]
    },
    
    async createGuest() {
      this.creatingGuest = true
      try {
        // Mock API call for now
        await new Promise(resolve => setTimeout(resolve, 1000))
        this.showNewGuestModal = false
        this.$resources.guests.fetch()
        this.resetNewGuestForm()
      } catch (error) {
        console.error('Error creating guest:', error)
      } finally {
        this.creatingGuest = false
      }
    },
    
    resetNewGuestForm() {
      this.newGuest = {
        guest_name: '',
        email: '',
        phone: '',
        address: '',
        nationality: '',
        id_type: '',
        id_number: ''
      }
    }
  }
}
</script>

<style scoped>
.frappe-app-page {
  padding: 1.5rem;
  background: var(--bg-color);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  margin-bottom: 1.5rem;
}

.card-body {
  padding: 1.5rem;
}

.control-label {
  display: block;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.25rem;
  background: var(--control-bg);
  color: var(--text-color);
}

.input-group {
  display: flex;
}

.input-group-addon {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-left: none;
  background: var(--gray-100);
  color: var(--text-muted);
}

.guest-grid {
  min-height: 400px;
}

.guest-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.guest-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.guest-avatar {
  text-align: center;
  margin-bottom: 1rem;
  position: relative;
}

.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: 500;
  color: white;
}

.avatar-lg {
  width: 4rem;
  height: 4rem;
  font-size: 1.25rem;
}

.avatar-xl {
  width: 6rem;
  height: 6rem;
  font-size: 1.5rem;
}

.avatar-text {
  color: white;
}

.bg-primary {
  background: var(--primary);
}

.guest-status {
  margin-top: 0.5rem;
  font-size: 0.75rem;
}

.guest-info {
  text-align: center;
  margin-bottom: 1rem;
}

.guest-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.75rem;
}

.guest-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.detail-item svg {
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.guest-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn-default {
  background: var(--card-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-primary {
  background: var(--primary);
  color: white;
  border: 1px solid var(--primary);
}

.btn-success {
  background: var(--green);
  color: white;
  border: 1px solid var(--green);
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-success {
  background: var(--green);
  color: white;
}

.badge-secondary {
  background: var(--gray-500);
  color: white;
}

.badge-primary {
  background: var(--blue);
  color: white;
}

.badge-warning {
  background: var(--orange);
  color: white;
}

.badge-danger {
  background: var(--red);
  color: white;
}

.guest-details {
  padding: 1rem 0;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section h4 {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-weight: 500;
  color: var(--text-muted);
}

.detail-value {
  color: var(--text-color);
}

.booking-history {
  margin-top: 1rem;
}

.booking-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.booking-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--gray-50);
  border-radius: 0.375rem;
}

.booking-info {
  flex: 1;
}

.booking-title {
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.booking-dates {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.booking-status {
  margin-bottom: 0.25rem;
}

.booking-amount {
  font-weight: 600;
  color: var(--text-color);
}

.form-group {
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  margin-top: 2rem;
}

.text-center {
  text-align: center;
}

.text-muted {
  color: var(--text-muted);
}

.py-8 {
  padding-top: 2rem;
  padding-bottom: 2rem;
}
</style>
