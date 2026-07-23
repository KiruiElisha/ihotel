import { createApp } from 'vue'
import { FrappeUI, frappeRequest, setConfig } from 'frappe-ui'

import App from './App.vue'
import router from './router'
import './index.css'

// Without this, createResource posts to a relative URL instead of /api/method.
setConfig('resourceFetcher', frappeRequest)

const app = createApp(App)
// No realtime features here, and the socket lives on a different port than the
// web server, so connecting only produces CORS noise in the console.
app.use(FrappeUI, { socketio: false })
app.use(router)
app.mount('#app')
