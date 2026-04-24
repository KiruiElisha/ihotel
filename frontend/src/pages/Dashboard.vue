<template>
  <div class="frappe-app-page">
    <div class="frappe-container">
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-title">Dashboard</div>
        <div class="page-actions">
          <Button 
            icon="refresh" 
            @click="refreshData"
            :loading="loading"
          >
            Refresh
          </Button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row">
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon available">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Available Rooms</div>
              <div class="stat-value">{{ stats.available_rooms }}</div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon occupied">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Occupied Rooms</div>
              <div class="stat-value">{{ stats.occupied_rooms }}</div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon checkouts">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Check-outs Today</div>
              <div class="stat-value">{{ stats.checkouts_today }}</div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon revenue">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Revenue Today</div>
              <div class="stat-value">{{ formatCurrency(stats.revenue_today) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity & Quick Actions -->
      <div class="row">
        <div class="col-md-8">
          <div class="card">
            <div class="card-header">
              <div class="card-title">Recent Activity</div>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-4">
                <LoadingText />
              </div>
              <div v-else-if="recent_activities.length === 0" class="text-muted text-center py-4">
                No recent activity
              </div>
              <div v-else class="activity-list">
                <div 
                  v-for="activity in recent_activities" 
                  :key="activity.name"
                  class="activity-item"
                >
                  <div class="activity-icon">
                    <ActivityIcon :type="activity.activity_type" />
                  </div>
                  <div class="activity-content">
                    <div class="activity-title">{{ activity.title }}</div>
                    <div class="activity-description">{{ activity.description }}</div>
                    <div class="activity-time">{{ formatTime(activity.creation) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card">
            <div class="card-header">
              <div class="card-title">Quick Actions</div>
            </div>
            <div class="card-body">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Button, LoadingText } from 'frappe-ui'

export default {
  name: 'Dashboard',
  components: {
    Button,
    LoadingText,
    ActivityIcon: {
      props: ['type'],
      template: `
        <div class="activity-icon-wrapper">
          <svg v-if="type === 'check_in'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <svg v-else-if="type === 'check_out'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 17l-4 4m0 0l-4-4m4 4V3"/>
          </svg>
          <svg v-else-if="type === 'housekeeping'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
      `
    }
  },
  data() {
    return {
      loading: false,
      stats: {
        available_rooms: 0,
        occupied_rooms: 0,
        checkouts_today: 0,
        revenue_today: 0
      },
      recent_activities: []
    }
  },
  resources: {
    dashboard_stats: {
      url: 'ihotel.api.get_dashboard_stats',
      auto: true
    },
    recent_activities: {
      url: 'ihotel.api.get_recent_activities',
      auto: true
    }
  },
  watch: {
    '$resources.dashboard_stats.data'(newData) {
      if (newData) {
        this.stats = newData
      }
    },
    '$resources.recent_activities.data'(newData) {
      if (newData) {
        this.recent_activities = newData
      }
    }
  },
  methods: {
    refreshData() {
      this.loading = true
      Promise.all([
        this.$resources.dashboard_stats.fetch(),
        this.$resources.recent_activities.fetch()
      ]).finally(() => {
        this.loading = false
      })
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount || 0)
    },
    
    formatTime(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now - date
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMins / 60)
      
      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins} mins ago`
      if (diffHours < 24) return `${diffHours} hours ago`
      return date.toLocaleDateString()
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

.stat-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  color: white;
}

.stat-icon.available {
  background: var(--green);
}

.stat-icon.occupied {
  background: var(--blue);
}

.stat-icon.checkouts {
  background: var(--orange);
}

.stat-icon.revenue {
  background: var(--purple);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  margin-bottom: 1rem;
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

.activity-list {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  padding: 1rem 0;
  border-bottom: 1px solid var(--border-color);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon-wrapper {
  width: 2rem;
  height: 2rem;
  background: var(--gray-100);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.activity-description {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.activity-time {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.quick-actions .btn {
  margin-bottom: 0.75rem;
}

.btn-block {
  display: block;
  width: 100%;
}

.btn-primary {
  background: var(--primary);
  color: white;
  border: 1px solid var(--primary);
}

.btn-default {
  background: var(--card-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.text-center {
  text-align: center;
}

.text-muted {
  color: var(--text-muted);
}

.py-4 {
  padding-top: 1rem;
  padding-bottom: 1rem;
}
</style>