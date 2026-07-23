import { onMounted, onUnmounted, ref } from 'vue'

/** Reactive flag: true when the viewport is below `bp` px (Tailwind md by default). */
export function useIsMobile(bp = 768) {
  const isMobile = ref(false)
  const update = () => (isMobile.value = window.innerWidth < bp)

  onMounted(() => {
    update()
    window.addEventListener('resize', update)
  })
  onUnmounted(() => window.removeEventListener('resize', update))

  return isMobile
}
