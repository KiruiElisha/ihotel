<template>
  <div class="frappe-app-page">
    <div class="frappe-container">
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-title">Room Board</div>
        <div class="page-actions">
          <Button 
            icon="refresh" 
            @click="refreshRooms"
            :loading="$resources.room_data.loading"
          >
            Refresh
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
                  placeholder="Search room number or guest..."
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
              <label class="control-label">Room Type</label>
              <select v-model="selectedRoomType" class="form-control">
                <option value="">All Room Types</option>
                <option v-for="type in roomTypes" :key="type" :value="type">{{ type }}</option>
              </select>
            </div>
            
            <div class="col-md-2">
              <label class="control-label">Floor</label>
              <select v-model="selectedFloor" class="form-control">
                <option value="">All Floors</option>
                <option v-for="floor in floors" :key="floor" :value="floor">Floor {{ floor }}</option>
              </select>
            </div>
            
            <div class="col-md-2">
              <label class="control-label">Status</label>
              <select v-model="selectedStatus" class="form-control">
                <option value="">All Statuses</option>
                <option v-for="status in statusOptions" :key="status.value" :value="status.value">{{ status.label }}</option>
              </select>
            </div>
            
            <div class="col-md-3">
              <label class="control-label">&nbsp;</label>
              <div>
                <Button @click="clearFilters" icon="x">Clear Filters</Button>
              </div>
            </div>
          </div>

          <!-- Status Pills -->
          <div class="status-pills">
            <button 
              v-for="status in statusOptions" 
              :key="status.value"
              @click="selectedStatus = selectedStatus === status.value ? '' : status.value"
              :class="[
                'status-pill',
                selectedStatus === status.value ? 'active' : ''
              ]"
            >
              <span class="status-dot" :style="{ backgroundColor: status.color }"></span>
              {{ status.label }}
              <span class="status-count">{{ getStatusCount(status.value) }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Room Grid -->
      <div class="room-grid">
        <div v-if="$resources.room_data.loading" class="text-center py-8">
          <LoadingText />
        </div>
        <div v-else-if="filteredRooms.length === 0" class="text-muted text-center py-8">
          No rooms match the current filters
        </div>
        <div v-else class="room-cards">
          <div 
            v-for="room in filteredRooms" 
            :key="room.name"
            @click="selectRoom(room)"
            :class="[
              'room-card',
              `status-${room.status.toLowerCase().replace(' ', '-')}`
            ]"
          >
            <div class="room-header">
              <div class="room-number">{{ room.room_number }}</div>
              <div class="room-status" :style="{ backgroundColor: getStatusColor(room.status) }"></div>
            </div>
            
            <div class="room-type">{{ room.room_type }}</div>
            <div class="room-floor">Floor {{ room.floor }}</div>
            
            <div class="room-status-label" :style="{ color: getStatusColor(room.status) }">
              {{ room.status }}
            </div>
            
            <div v-if="room.guest" class="room-guest">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              {{ room.guest }}
            </div>
            
            <div v-if="room.check_out" class="room-checkout">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              Out: {{ formatDate(room.check_out) }}
            </div>
            
            <div v-if="room.status === 'Available'" class="room-actions">
              <Button 
                @click.stop="quickCheckIn(room)"
                class="btn-success btn-sm"
                icon="log-in"
              >
                Check In
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Room Details Modal -->
      <Dialog v-model="showRoomDetails" :title="`Room ${selectedRoom?.room_number}`">
        <div v-if="selectedRoom" class="room-details">
          <div class="detail-row">
            <span class="detail-label">Type:</span>
            <span class="detail-value">{{ selectedRoom.room_type }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Floor:</span>
            <span class="detail-value">{{ selectedRoom.floor }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value status-badge" :style="{ backgroundColor: getStatusColor(selectedRoom.status) + '20', color: getStatusColor(selectedRoom.status) }">
              {{ selectedRoom.status }}
            </span>
          </div>
          <div v-if="selectedRoom.guest" class="detail-row">
            <span class="detail-label">Guest:</span>
            <span class="detail-value">{{ selectedRoom.guest }}</span>
          </div>
          <div v-if="selectedRoom.check_out" class="detail-row">
            <span class="detail-label">Check Out:</span>
            <span class="detail-value">{{ formatDate(selectedRoom.check_out) }}</span>
          </div>
        </div>
        
        <template #actions>
          <Button 
            v-if="selectedRoom?.status === 'Available'"
            @click="quickCheckIn(selectedRoom)"
            class="btn-success"
            icon="log-in"
          >
            Check In Guest
          </Button>
          <Button 
            v-if="selectedRoom?.status === 'Occupied'"
            @click="checkOut(selectedRoom)"
            class="btn-danger"
            icon="log-out"
          >
            Check Out
          </Button>
          <Button class="btn-default" icon="info">View Details</Button>
        </template>
      </Dialog>
    </div>
  </div>
</template>

<script>
import { Button, Dialog, LoadingText } from 'frappe-ui'

export default {
  name: 'RoomBoard',
  components: {
    Button,
    Dialog,
    LoadingText
  },
  data() {
    return {
      searchQuery: '',
      selectedRoomType: '',
      selectedFloor: '',
      selectedStatus: '',
      selectedRoom: null,
      showRoomDetails: false,
      statusOptions: [
        { value: 'Available', label: 'Available', color: '#10b981' },
        { value: 'Occupied', label: 'Occupied', color: '#3b82f6' },
        { value: 'Vacant Dirty', label: 'Vacant Dirty', color: '#fb923c' },
        { value: 'Vacant Clean', label: 'Vacant Clean', color: '#34d399' },
        { value: 'Out of Order', label: 'Out of Order', color: '#ef4444' },
      ]
    }
  },
  resources: {
    room_data: {
      url: 'ihotel.api.get_room_board_data',
      auto: true
    }
  },
  computed: {
    rooms() {
      return this.$resources.room_data.data || []
    },
    filteredRooms() {
      return this.rooms.filter(room => {
        const matchesSearch = !this.searchQuery || 
          room.room_number.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          (room.guest && room.guest.toLowerCase().includes(this.searchQuery.toLowerCase()))
        
        const matchesType = !this.selectedRoomType || room.room_type === this.selectedRoomType
        const matchesFloor = !this.selectedFloor || room.floor.toString() === this.selectedFloor
        const matchesStatus = !this.selectedStatus || room.status === this.selectedStatus
        
        return matchesSearch && matchesType && matchesFloor && matchesStatus
      })
    },
    roomTypes() {
      const types = [...new Set(this.rooms.map(room => room.room_type))]
      return types.filter(Boolean).sort()
    },
    floors() {
      const floors = [...new Set(this.rooms.map(room => room.floor))]
      return floors.filter(Boolean).sort((a, b) => a - b)
    }
  },
  methods: {
    getStatusColor(status) {
      const statusMap = {
        'Available': '#10b981',
        'Occupied': '#3b82f6',
        'Vacant Dirty': '#fb923c',
        'Vacant Clean': '#34d399',
        'Out of Order': '#ef4444',
      }
      return statusMap[status] || '#6b7280'
    },
    
    getStatusCount(status) {
      return this.rooms.filter(room => room.status === status).length
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    
    selectRoom(room) {
      this.selectedRoom = room
      this.showRoomDetails = true
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.selectedRoomType = ''
      this.selectedFloor = ''
      this.selectedStatus = ''
    },
    
    quickCheckIn(room) {
      this.showRoomDetails = false
      // Check-in functionality
      alert(`Check-in for room ${room.room_number}`)
    },
    
    checkOut(room) {
      this.showRoomDetails = false
      // Process check-out
      this.$resources.check_out_room.submit({
        room: room.name
      }).then(() => {
        this.$resources.room_data.fetch()
      })
    },
    
    refreshRooms() {
      this.$resources.room_data.fetch()
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

.status-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.status-pill {
  display: flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  background: var(--card-bg);
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.2s;
}

.status-pill:hover {
  background: var(--gray-100);
}

.status-pill.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.status-count {
  margin-left: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.125rem 0.375rem;
  border-radius: 1rem;
  font-size: 0.75rem;
}

.room-grid {
  min-height: 400px;
}

.room-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.room-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 4px solid transparent;
}

.room-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.room-card.status-available {
  border-left-color: var(--green);
}

.room-card.status-occupied {
  border-left-color: var(--blue);
}

.room-card.status-vacant-dirty {
  border-left-color: var(--orange);
}

.room-card.status-vacant-clean {
  border-left-color: var(--green);
}

.room-card.status-out-of-order {
  border-left-color: var(--red);
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.room-number {
  font-weight: 600;
  color: var(--text-color);
}

.room-status {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
}

.room-type {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.room-floor {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

.room-status-label {
  font-size: 0.75rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.room-guest,
.room-checkout {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.room-guest svg,
.room-checkout svg {
  margin-right: 0.25rem;
  color: var(--text-muted);
}

.room-actions {
  margin-top: 0.75rem;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
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

.btn-default {
  background: var(--card-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.room-details {
  padding: 1rem 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-color);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 500;
  color: var(--text-muted);
}

.detail-value {
  color: var(--text-color);
}

.status-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
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