<template>
  <div class="frappe-app-page">
    <div class="frappe-container">
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-title">Housekeeping</div>
        <div class="page-actions">
          <Button 
            icon="plus" 
            @click="showNewTaskModal = true"
            class="btn-primary"
          >
            New Task
          </Button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon pending">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Pending Tasks</div>
              <div class="stat-value">{{ stats.pending_tasks }}</div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon in-progress">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">In Progress</div>
              <div class="stat-value">{{ stats.in_progress_tasks }}</div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon completed">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Completed Today</div>
              <div class="stat-value">{{ stats.completed_today }}</div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon overdue">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Overdue</div>
              <div class="stat-value">{{ stats.overdue_tasks }}</div>
            </div>
          </div>
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
                  placeholder="Search tasks..."
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
                <option value="Pending">Pending</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>
            
            <div class="col-md-2">
              <label class="control-label">Priority</label>
              <select v-model="selectedPriority" class="form-control">
                <option value="">All Priorities</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            
            <div class="col-md-2">
              <label class="control-label">Task Type</label>
              <select v-model="selectedTaskType" class="form-control">
                <option value="">All Types</option>
                <option v-for="type in taskTypes" :key="type" :value="type">{{ type }}</option>
              </select>
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

      <!-- Task Boards -->
      <div class="task-boards">
        <div v-if="$resources.tasks.loading" class="text-center py-8">
          <LoadingText />
        </div>
        <div v-else class="row">
          <!-- Pending Tasks -->
          <div class="col-md-4">
            <div class="task-board">
              <div class="board-header">
                <h4>Pending ({{ pendingTasks.length }})</h4>
                <div class="board-count badge badge-warning">{{ pendingTasks.length }}</div>
              </div>
              <div class="board-content">
                <div 
                  v-for="task in pendingTasks" 
                  :key="task.name"
                  class="task-card"
                  @click="selectTask(task)"
                >
                  <div class="task-header">
                    <div class="task-priority" :class="getPriorityClass(task.priority)">
                      {{ task.priority }}
                    </div>
                    <div class="task-time">{{ formatTime(task.creation) }}</div>
                  </div>
                  
                  <div class="task-title">{{ task.task_type }}</div>
                  <div class="task-room">Room {{ getRoomNumber(task.room) }}</div>
                  
                  <div v-if="task.notes" class="task-notes">
                    {{ task.notes }}
                  </div>
                  
                  <div class="task-actions">
                    <Button 
                      @click.stop="startTask(task)"
                      class="btn-success btn-sm"
                      icon="play"
                    >
                      Start
                    </Button>
                    <Button 
                      @click.stop="editTask(task)"
                      class="btn-default btn-sm"
                      icon="edit"
                    >
                      Edit
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- In Progress Tasks -->
          <div class="col-md-4">
            <div class="task-board">
              <div class="board-header">
                <h4>In Progress ({{ inProgressTasks.length }})</h4>
                <div class="board-count badge badge-primary">{{ inProgressTasks.length }}</div>
              </div>
              <div class="board-content">
                <div 
                  v-for="task in inProgressTasks" 
                  :key="task.name"
                  class="task-card in-progress"
                  @click="selectTask(task)"
                >
                  <div class="task-header">
                    <div class="task-priority" :class="getPriorityClass(task.priority)">
                      {{ task.priority }}
                    </div>
                    <div class="task-time">{{ formatTime(task.creation) }}</div>
                  </div>
                  
                  <div class="task-title">{{ task.task_type }}</div>
                  <div class="task-room">Room {{ getRoomNumber(task.room) }}</div>
                  <div class="task-assignee">Assigned to: {{ getAssigneeName(task.assigned_to) }}</div>
                  
                  <div v-if="task.notes" class="task-notes">
                    {{ task.notes }}
                  </div>
                  
                  <div class="task-actions">
                    <Button 
                      @click.stop="completeTask(task)"
                      class="btn-success btn-sm"
                      icon="check"
                    >
                      Complete
                    </Button>
                    <Button 
                      @click.stop="pauseTask(task)"
                      class="btn-warning btn-sm"
                      icon="pause"
                    >
                      Pause
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Completed Tasks -->
          <div class="col-md-4">
            <div class="task-board">
              <div class="board-header">
                <h4>Completed ({{ completedTasks.length }})</h4>
                <div class="board-count badge badge-success">{{ completedTasks.length }}</div>
              </div>
              <div class="board-content">
                <div 
                  v-for="task in completedTasks" 
                  :key="task.name"
                  class="task-card completed"
                  @click="selectTask(task)"
                >
                  <div class="task-header">
                    <div class="task-priority" :class="getPriorityClass(task.priority)">
                      {{ task.priority }}
                    </div>
                    <div class="task-time">{{ formatTime(task.completion_time) }}</div>
                  </div>
                  
                  <div class="task-title">{{ task.task_type }}</div>
                  <div class="task-room">Room {{ getRoomNumber(task.room) }}</div>
                  <div class="task-completed-by">Completed by: {{ getAssigneeName(task.assigned_to) }}</div>
                  
                  <div v-if="task.notes" class="task-notes">
                    {{ task.notes }}
                  </div>
                  
                  <div class="task-actions">
                    <Button 
                      @click.stop="reopenTask(task)"
                      class="btn-default btn-sm"
                      icon="refresh"
                    >
                      Reopen
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Task Details Modal -->
      <Dialog v-model="showTaskDetails" :title="`Task: ${selectedTask?.task_type}`" size="large">
        <div v-if="selectedTask" class="task-details">
          <div class="row">
            <div class="col-md-6">
              <div class="detail-section">
                <h4>Task Information</h4>
                <div class="detail-list">
                  <div class="detail-item">
                    <span class="detail-label">Task Type:</span>
                    <span class="detail-value">{{ selectedTask.task_type }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Room:</span>
                    <span class="detail-value">{{ getRoomNumber(selectedTask.room) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Priority:</span>
                    <span class="detail-value">
                      <span :class="['badge', getPriorityClass(selectedTask.priority)]">
                        {{ selectedTask.priority }}
                      </span>
                    </span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Status:</span>
                    <span class="detail-value">
                      <span :class="['badge', getStatusClass(selectedTask.status)]">
                        {{ selectedTask.status }}
                      </span>
                    </span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Assigned To:</span>
                    <span class="detail-value">{{ getAssigneeName(selectedTask.assigned_to) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Created:</span>
                    <span class="detail-value">{{ formatDateTime(selectedTask.creation) }}</span>
                  </div>
                  <div class="detail-item" v-if="selectedTask.completion_time">
                    <span class="detail-label">Completed:</span>
                    <span class="detail-value">{{ formatDateTime(selectedTask.completion_time) }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="detail-section">
                <h4>Notes</h4>
                <div class="task-notes-full">
                  {{ selectedTask.notes || 'No notes provided' }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <template #actions>
          <Button 
            v-if="selectedTask?.status === 'Pending'"
            @click="startTask(selectedTask)"
            class="btn-success"
            icon="play"
          >
            Start Task
          </Button>
          <Button 
            v-if="selectedTask?.status === 'In Progress'"
            @click="completeTask(selectedTask)"
            class="btn-success"
            icon="check"
          >
            Complete Task
          </Button>
          <Button 
            v-if="selectedTask?.status === 'Completed'"
            @click="reopenTask(selectedTask)"
            class="btn-default"
            icon="refresh"
          >
            Reopen Task
          </Button>
          <Button 
            @click="editTask(selectedTask)"
            class="btn-primary"
            icon="edit"
          >
            Edit Task
          </Button>
        </template>
      </Dialog>

      <!-- New Task Modal -->
      <Dialog v-model="showNewTaskModal" title="Create New Task">
        <form @submit.prevent="createTask" class="task-form">
          <div class="row">
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Task Type *</label>
                <select v-model="newTask.task_type" required class="form-control">
                  <option value="">Select Task Type</option>
                  <option value="Room Cleaning">Room Cleaning</option>
                  <option value="Maintenance">Maintenance</option>
                  <option value="Laundry">Laundry</option>
                  <option value="Room Service">Room Service</option>
                  <option value="Deep Cleaning">Deep Cleaning</option>
                </select>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Room *</label>
                <select v-model="newTask.room" required class="form-control">
                  <option value="">Select Room</option>
                  <option v-for="room in availableRooms" :key="room.name" :value="room.name">
                    {{ room.room_number }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Priority</label>
                <select v-model="newTask.priority" class="form-control">
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="form-group">
                <label class="control-label">Assign To</label>
                <select v-model="newTask.assigned_to" class="form-control">
                  <option value="">Unassigned</option>
                  <option v-for="staff in housekeepingStaff" :key="staff.name" :value="staff.name">
                    {{ staff.employee_name }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="col-md-12">
              <div class="form-group">
                <label class="control-label">Notes</label>
                <textarea 
                  v-model="newTask.notes" 
                  rows="4"
                  class="form-control"
                  placeholder="Add any additional notes..."
                ></textarea>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <Button type="button" @click="showNewTaskModal = false" class="btn-default">
              Cancel
            </Button>
            <Button type="submit" class="btn-primary" :loading="creatingTask">
              Create Task
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
  name: 'Housekeeping',
  components: {
    Button,
    Dialog,
    LoadingText
  },
  data() {
    return {
      searchQuery: '',
      selectedStatus: '',
      selectedPriority: '',
      selectedTaskType: '',
      showNewTaskModal: false,
      showTaskDetails: false,
      selectedTask: null,
      creatingTask: false,
      newTask: {
        task_type: '',
        room: '',
        priority: 'Medium',
        assigned_to: '',
        notes: ''
      },
      availableRooms: [],
      housekeepingStaff: []
    }
  },
  resources: {
    tasks: {
      url: 'ihotel.api.get_housekeeping_tasks',
      auto: true
    },
    rooms: {
      url: 'ihotel.api.get_rooms',
      auto: true
    },
    create_task: {
      method: 'POST',
      url: 'ihotel.api.create_housekeeping_task'
    }
  },
  computed: {
    tasks() {
      return this.$resources.tasks.data || []
    },
    filteredTasks() {
      return this.tasks.filter(task => {
        const matchesSearch = !this.searchQuery || 
          task.task_type.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          task.notes.toLowerCase().includes(this.searchQuery.toLowerCase())
        
        const matchesStatus = !this.selectedStatus || task.status === this.selectedStatus
        const matchesPriority = !this.selectedPriority || task.priority === this.selectedPriority
        const matchesType = !this.selectedTaskType || task.task_type === this.selectedTaskType
        
        return matchesSearch && matchesStatus && matchesPriority && matchesType
      })
    },
    pendingTasks() {
      return this.filteredTasks.filter(task => task.status === 'Pending')
    },
    inProgressTasks() {
      return this.filteredTasks.filter(task => task.status === 'In Progress')
    },
    completedTasks() {
      return this.filteredTasks.filter(task => task.status === 'Completed')
    },
    stats() {
      return {
        pending_tasks: this.tasks.filter(t => t.status === 'Pending').length,
        in_progress_tasks: this.tasks.filter(t => t.status === 'In Progress').length,
        completed_today: this.tasks.filter(t => {
          return t.status === 'Completed' && t.completion_time && 
                 new Date(t.completion_time).toDateString() === new Date().toDateString()
        }).length,
        overdue_tasks: this.tasks.filter(t => {
          return t.status !== 'Completed' && t.creation && 
                 new Date(t.creation) < new Date(Date.now() - 24 * 60 * 60 * 1000)
        }).length
      }
    },
    taskTypes() {
      const types = [...new Set(this.tasks.map(t => t.task_type))]
      return types.filter(Boolean).sort()
    }
  },
  watch: {
    '$resources.rooms.data'(newData) {
      if (newData) {
        this.availableRooms = newData
      }
    }
  },
  created() {
    // Mock housekeeping staff data
    this.housekeepingStaff = [
      { name: 'staff1', employee_name: 'John Smith' },
      { name: 'staff2', employee_name: 'Sarah Johnson' },
      { name: 'staff3', employee_name: 'Mike Davis' }
    ]
  },
  methods: {
    getRoomNumber(roomId) {
      const room = this.availableRooms.find(r => r.name === roomId)
      return room?.room_number || roomId
    },
    
    getAssigneeName(assigneeId) {
      const staff = this.housekeepingStaff.find(s => s.name === assigneeId)
      return staff?.employee_name || 'Unassigned'
    },
    
    getPriorityClass(priority) {
      const classes = {
        'High': 'badge-danger',
        'Medium': 'badge-warning',
        'Low': 'badge-success'
      }
      return classes[priority] || 'badge-secondary'
    },
    
    getStatusClass(status) {
      const classes = {
        'Pending': 'badge-warning',
        'In Progress': 'badge-primary',
        'Completed': 'badge-success',
        'Cancelled': 'badge-danger'
      }
      return classes[status] || 'badge-secondary'
    },
    
    formatTime(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    },
    
    formatDateTime(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.selectedStatus = ''
      this.selectedPriority = ''
      this.selectedTaskType = ''
    },
    
    selectTask(task) {
      this.selectedTask = task
      this.showTaskDetails = true
    },
    
    startTask(task) {
      this.showTaskDetails = false
      // Update task status to In Progress
      task.status = 'In Progress'
      alert(`Started task: ${task.task_type}`)
    },
    
    completeTask(task) {
      this.showTaskDetails = false
      // Update task status to Completed
      task.status = 'Completed'
      task.completion_time = new Date().toISOString()
      alert(`Completed task: ${task.task_type}`)
    },
    
    pauseTask(task) {
      // Update task status back to Pending
      task.status = 'Pending'
      alert(`Paused task: ${task.task_type}`)
    },
    
    reopenTask(task) {
      this.showTaskDetails = false
      // Update task status back to Pending
      task.status = 'Pending'
      task.completion_time = null
      alert(`Reopened task: ${task.task_type}`)
    },
    
    editTask(task) {
      this.selectedTask = task
      alert(`Edit task: ${task.task_type}`)
    },
    
    async createTask() {
      this.creatingTask = true
      try {
        // Mock API call for now
        await new Promise(resolve => setTimeout(resolve, 1000))
        this.showNewTaskModal = false
        this.$resources.tasks.fetch()
        this.resetNewTaskForm()
      } catch (error) {
        console.error('Error creating task:', error)
      } finally {
        this.creatingTask = false
      }
    },
    
    resetNewTaskForm() {
      this.newTask = {
        task_type: '',
        room: '',
        priority: 'Medium',
        assigned_to: '',
        notes: ''
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

.stat-icon.pending {
  background: var(--orange);
}

.stat-icon.in-progress {
  background: var(--blue);
}

.stat-icon.completed {
  background: var(--green);
}

.stat-icon.overdue {
  background: var(--red);
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

.task-boards {
  min-height: 600px;
}

.task-board {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  height: 600px;
  display: flex;
  flex-direction: column;
}

.board-header {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.board-header h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.board-count {
  font-size: 0.75rem;
}

.board-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

.task-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.task-card:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.task-card.in-progress {
  border-left: 4px solid var(--blue);
}

.task-card.completed {
  border-left: 4px solid var(--green);
  opacity: 0.7;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.task-priority {
  font-size: 0.75rem;
  font-weight: 500;
}

.task-time {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.task-title {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.task-room {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.task-assignee,
.task-completed-by {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.task-notes {
  font-size: 0.875rem;
  color: var(--text-color);
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
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

.btn-warning {
  background: var(--orange);
  color: white;
  border: 1px solid var(--orange);
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

.task-details {
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

.task-notes-full {
  background: var(--gray-50);
  padding: 1rem;
  border-radius: 0.375rem;
  color: var(--text-color);
  line-height: 1.5;
  min-height: 100px;
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
