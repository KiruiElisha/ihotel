import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'
import path from 'path'

export default defineConfig({
  plugins: [
    frappeui({
      frontendRoute: '/hotel',
      frappeProxy: true,
      lucideIcons: true,
      jinjaBootData: true,
      buildConfig: {
        outDir: '../ihotel/public/hotel',
        baseUrl: '/assets/ihotel/hotel/',
        indexHtmlPath: '../ihotel/www/hotel.html',
        emptyOutDir: true,
        sourcemap: false,
      },
    }),
    vue(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        // Keep the framework and the UI kit together in ONE vendor chunk.
        //
        // frappe-ui imports vue and vue-router, so splitting them into separate
        // chunks makes those chunks reference each other's live bindings and
        // Rollup emits a circular-chunk temporal-dead-zone crash at load time
        // ("can't access lexical declaration '…' before initialization").
        // A single vendor chunk still changes far less often than the pages, so
        // browsers keep it cached across deploys — without the cycle.
        manualChunks(id) {
          if (!id.includes('node_modules')) return
          if (/[\\/](vue|vue-router|@vue|@vueuse|frappe-ui)[\\/]/.test(id)) {
            return 'vendor'
          }
        },
      },
    },
  },
})
