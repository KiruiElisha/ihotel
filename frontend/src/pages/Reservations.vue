<template>
  <div class="frappe-app-page">
    <div class="frappe-container">
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-title">Reservations</div>
        <div class="page-actions">
          <Button 
            icon="plus" 
            @click="showNewReservationModal = true"
            class="btn-primary"
          >
            New Reservation
          </Button>
        </div>
      </div>

      <!-- Filters -->
      <div class="card">
        <div class="card-body">
          <div class="row">
            <div class="col-md-3">
              <label class="control-label">Search</label>
              <div class="input-group">
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search guest or reservation..."
                  class="form-control"
                >
                <div class="input-group-addon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                  </svg>
                </div>
              </div>
            </div>
            
            <div class="col-md-2">
              <label class="control-label">Status</label>
              <select v-model="selectedStatus" class="form-control">
                <option value="">All Statuses</option>
                <option value="Confirmed">Confirmed</option>
                <option value="Pending">Pending</option>
                <option value="Cancelled">Cancelled</option>
                <option value="Checked In">Checked In</option>
                <option value="Checked Out">Checked Out</option>
              </select>
            </div>
            
            <div class="col-md-2">
              <label class="control-label">Room Type</label>
              <select v-model="selectedRoomType" class="form-control">
                <option value="">All Room Types</option>
                <option v-for="type in roomTypes" :key="type" :value="type">{{ type }}</option>
              </select>
            </div>
            
            <div class="col-md-2">
              <label class="control-label">Date Range</label>
              <input 
                v-model="dateRange" 
                type="text" 
                placeholder="Select date range"
                class="form-control"
              >
            </div>
            
            <div class="col-md-3">
              <label class="control-label">&nbsp;</label>
              <div>
                <Button @click="clearFilters" icon="x">Clear Filters</Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reservations Table -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">All Reservations</div>
        </div>
        <div class="card-body p-0">
          <div v-if="$resources.reservations.loading" class="text-center py-8">
            <LoadingText />
          </div>
          <div v-else-if="filteredReservations.length === 0" class="text-muted text-center py-8">
            No reservations match the current filters
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Reservation ID</th>
                  <th>Guest</th>
                  <th>Room Type</th>
                  <th>Check-in</th>
                  <th>Check-out</th>
                  <th>Status</th>
                  <th>Amount</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="reservation in filteredReservations" :key="reservation.name">
                  <td class="text-medium">{{ reservation.name }}</td>
                  <td>
                    <div class="d-flex align-items-center">
                      <div class="avatar avatar-sm bg-gray-100 me-2">
                        <span class="avatar-text">{{ getGuestInitials(reservation.guest) }}</span>
                      </div>
                      <div>
                        <div class="text-medium">{{ getGuestName(reservation.guest) }}</div>
                        <div class="text-muted text-small">{{ getGuestEmail(reservation.guest) }}</div>
                      </div>
                    </div>
                  </td>
                  <td>{{ reservation.room_type }}</td>
                  <td>{{ formatDate(reservation.arrival_date) }}</td>
                  <td>{{ formatDate(reservation.departure_date) }}</td>
                  <td>
                    <span :class="getStatusClass(reservation.status)">
                      {{ reservation.status }}
                    </span>
                  </td>
                  <td class="text-medium">{{ formatCurrency(reservation.total_amount) }}</td>
                  <td>
                    <div class="btn-group">
                      <Button 
                        @click="viewReservation(reservation)" 
                        class="btn-default btn-sm"
                        icon="eye"
                      >
                        View
                      </Button>
                      <Button 
                        v-if="reservation.status === 'Confirmed'"
                        @click="checkIn(reservation)" 
                        class="btn-success btn-sm"
                        icon="log-in"
                      >
                        Check In
                      </Button>
                      <Button 
                        v-if="reservation.status !== 'Cancelled' && reservation.status !== 'Checked Out'"
                        @click="cancelReservation(reservation)" 
                        class="btn-danger btn-sm"
                        icon="x"
                      >
                        Cancel
                      </Button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Reservation Details Modal -->
      <Dialog v-model="showReservationDetails" :title="`Reservation ${selectedReservation?.name}`" size="large">
        <div v-if="selectedReservation" class="reservation-details">
          <div class="row">
            <div class="col-md-6">
              <div class="detail-section">
                <h4>Guest Information</h4>
                <div class="detail-list">
                  <div class="detail-item">
                    <span class="detail-label">Name:</span>
                    <span class="detail-value">{{ getGuestName(selectedReservation.guest) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Email:</span>
                    <span class="detail-value">{{ getGuestEmail(selectedReservation.guest) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Phone:</span>
                    <span class="detail-value">{{ getGuestPhone(selectedReservation.guest) }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="detail-section">
                <h4>Reservation Details</h4>
                <div class="detail-list">
                  <div class="detail-item">
                    <span class="detail-label">Room Type:</span>
                    <span class="detail-value">{{ selectedReservation.room_type }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Check-in:</span>
                    <span class="detail-value">{{ formatDate(selectedReservation.arrival_date) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Check-out:</span>
                    <span class="detail-value">{{ formatDate(selectedReservation.departure_date) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Guests:</span>
                    <span class="detail-value">{{ selectedReservation.adults || 1 }} Adults, {{ selectedReservation.children || 0 }} Children</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Total Amount:</span>
                    <span class="detail-value text-medium">{{ formatCurrency(selectedReservation.total_amount) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <template #actions>
          <Button 
            v-if="selectedReservation?.status === 'Confirmed'"
            @click="checkIn(selectedReservation)"
            class="btn-success"
            icon="log-in"
          >
            Check In
          </Button>
          <Button 
            v-if="selectedReservation?.status !== 'Cancelled' && selectedReservation?.status !== 'Checked Out'"
            @click="cancelReservation(selectedReservation)"
            class="btn-danger"
            icon="x"
          >
            Cancel Reservation
          </Button>
        </template>
      </Dialog>

      <!-- New Reservation Modal -->
      <Dialog v-model="showNewReservationModal" title="New Reservation" size="large">
        <form @submit.prevent="createReservation" class="reservation-form">
          <div class="row">
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Guest Name</label>
                <input 
                  v-model="newReservation.guest_name" 
                  type="text" 
                  required
                  class="form-control"
                  placeholder="Enter guest name"
                >
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Email</label>
                <input 
                  v-model="newReservation.email" 
                  type="email" 
                  required
                  class="form-control"
                  placeholder="Enter email address"
                >
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Phone</label>
                <input 
                  v-model="newReservation.phone" 
                  type="tel" 
                  required
                  class="form-control"
                  placeholder="Enter phone number"
                >
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Room Type</label>
                <select v-model="newReservation.room_type" required class="form-control">
                  <option value="">Select Room Type</option>
                  <option v-for="type in roomTypes" :key="type" :value="type">{{ type }}</option>
                </select>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Check-in Date</label>
                <input 
                  v-model="newReservation.arrival_date" 
                  type="date" 
                  required
                  class="form-control"
                >
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Check-out Date</label>
                <input 
                  v-model="newReservation.departure_date" 
                  type="date" 
                  required
                  class="form-control"
                >
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Adults</label>
                <input 
                  v-model.number="newReservation.adults" 
                  type="number" 
                  min="1" 
                  required
                  class="form-control"
                >
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Children</label>
                <input 
                  v-model.number="newReservation.children" 
                  type="number" 
                  min="0" 
                  class="form-control"
                >
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <Button type="button" @click="showNewReservationModal = false" class="btn-default">
              Cancel
            </Button>
            <Button type="submit" class="btn-primary" :loading="creatingReservation">
              Create Reservation
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
  name: 'Reservations',
  components: {
    Button,
    Dialog,
    LoadingText
  },
  data() {
    return {
      searchQuery: '',
      selectedStatus: '',
      selectedRoomType: '',
      dateRange: '',
      showNewReservationModal: false,
      showReservationDetails: false,
      selectedReservation: null,
      creatingReservation: false,
      newReservation: {
        guest_name: '',
        email: '',
        phone: '',
        room_type: '',
        arrival_date: '',
        departure_date: '',
        adults: 1,
        children: 0
      },
      guests: []
    }
  },
  resources: {
    reservations: {
      url: 'ihotel.api.get_reservations',
      auto: true
    },
    guests: {
      url: 'ihotel.api.get_guests',
      auto: true
    }
  },
  computed: {
    reservations() {
      return this.$resources.reservations.data || []
    },
    filteredReservations() {
      return this.reservations.filter(reservation => {
        const matchesSearch = !this.searchQuery || 
          this.getGuestName(reservation.guest).toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          reservation.name.toLowerCase().includes(this.searchQuery.toLowerCase())
        
        const matchesStatus = !this.selectedStatus || reservation.status === this.selectedStatus
        const matchesRoomType = !this.selectedRoomType || reservation.room_type === this.selectedRoomType
        
        return matchesSearch && matchesStatus && matchesRoomType
      })
    },
    roomTypes() {
      const types = [...new Set(this.reservations.map(r => r.room_type))]
      return types.filter(Boolean).sort()
    }
  },
  watch: {
    '$resources.guests.data'(newData) {
      if (newData) {
        this.guests = newData
      }
    }
  },
  methods: {
    getGuestName(guestId) {
      const guest = this.guests.find(g => g.name === guestId)
      return guest?.guest_name || 'Unknown Guest'
    },
    
    getGuestEmail(guestId) {
      const guest = this.guests.find(g => g.name === guestId)
      return guest?.email || ''
    },
    
    getGuestPhone(guestId) {
      const guest = this.guests.find(g => g.name === guestId)
      return guest?.phone || ''
    },
    
    getGuestInitials(guestId) {
      const name = this.getGuestName(guestId)
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    },
    
    getStatusClass(status) {
      const statusClasses = {
        'Confirmed': 'badge badge-success',
        'Pending': 'badge badge-warning',
        'Cancelled': 'badge badge-danger',
        'Checked In': 'badge badge-primary',
        'Checked Out': 'badge badge-secondary',
      }
      return statusClasses[status] || 'badge badge-secondary'
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
    
    clearFilters() {
      this.searchQuery = ''
      this.selectedStatus = ''
      this.selectedRoomType = ''
      this.dateRange = ''
    },
    
    viewReservation(reservation) {
      this.selectedReservation = reservation
      this.showReservationDetails = true
    },
    
    checkIn(reservation) {
      this.showReservationDetails = false
      // Process check-in
      alert(`Check-in for reservation ${reservation.name}`)
    },
    
    cancelReservation(reservation) {
      this.showReservationDetails = false
      // Cancel reservation
      alert(`Cancelling reservation ${reservation.name}`)
    },
    
    async createReservation() {
      this.creatingReservation = true
      try {
        // Mock API call for now
        await new Promise(resolve => setTimeout(resolve, 1000))
        this.showNewReservationModal = false
        this.$resources.reservations.fetch()
        this.resetNewReservationForm()
      } catch (error) {
        console.error('Error creating reservation:', error)
      } finally {
        this.creatingReservation = false
      }
    },
    
    resetNewReservationForm() {
      this.newReservation = {
        guest_name: '',
        email: '',
        phone: '',
        room_type: '',
        arrival_date: '',
        departure_date: '',
        adults: 1,
        children: 0
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

.card-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.card-title {
  font-weight: 600;
  color: var(--text-color);
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

.table-responsive {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.table th {
  font-weight: 600;
  color: var(--text-muted);
  background: var(--gray-50);
}

.table-hover tbody tr:hover {
  background: var(--gray-50);
}

.text-medium {
  font-weight: 500;
}

.text-small {
  font-size: 0.875rem;
}

.text-muted {
  color: var(--text-muted);
}

.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: 500;
}

.avatar-sm {
  width: 2rem;
  height: 2rem;
  font-size: 0.75rem;
}

.avatar-text {
  color: var(--text-color);
}

.bg-gray-100 {
  background: var(--gray-100);
}

.me-2 {
  margin-right: 0.5rem;
}

.d-flex {
  display: flex;
}

.align-items-center {
  align-items: center;
}

.btn-group {
  display: flex;
  gap: 0.25rem;
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

.btn-success {
  background: var(--green);
  color: white;
  border: 1px solid var(--green);
}

.btn-danger {
  background: var(--red);
  color: white;
  border: 1px solid var(--red);
}

.btn-primary {
  background: var(--primary);
  color: white;
  border: 1px solid var(--primary);
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

.badge-warning {
  background: var(--orange);
  color: white;
}

.badge-danger {
  background: var(--red);
  color: white;
}

.badge-primary {
  background: var(--blue);
  color: white;
}

.badge-secondary {
  background: var(--gray-500);
  color: white;
}

.reservation-details {
  padding: 1rem 0;
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

.py-8 {
  padding-top: 2rem;
  padding-bottom: 2rem;
}
</style>
