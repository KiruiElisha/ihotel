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
        // Keep the framework and the UI kit in their own chunks: they change far
        // less often than the pages, so browsers keep them cached across deploys.
        manualChunks(id) {
          if (!id.includes('node_modules')) return
          if (id.includes('frappe-ui')) return 'frappe-ui'
          if (/[\\/](vue|vue-router|@vue)[\\/]/.test(id)) return 'vue'
        },
      },
    },
  },
})
