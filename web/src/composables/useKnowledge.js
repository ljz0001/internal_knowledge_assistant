import { computed, ref } from 'vue'
import { api } from '../api/client.js'

export function useKnowledge() {
  const documents = ref([])
  const stats = ref(null)
  const loading = ref(false)
  const error = ref('')
  const statsError = ref('')
  const loaded = ref(false)
  let pending
  let version = 0
  function reset() {
    version++; pending = null
    documents.value = []; stats.value = null; loaded.value = false
    error.value = ''; statsError.value = ''; loading.value = false
  }
  async function refresh() {
    if (pending) return pending
    const requestVersion = version
    loading.value = true
    error.value = ''; statsError.value = ''
    // 文档与向量统计独立更新，避免慢模型阻塞文档列表。
    pending = Promise.allSettled([
      api.documents().then((value) => {
        if (requestVersion === version) { documents.value = value || []; loaded.value = true }
      }).catch((e) => { if (requestVersion === version) error.value = e.message }),
      api.stats().then((value) => { if (requestVersion === version) stats.value = value })
        .catch((e) => { if (requestVersion === version) { stats.value = null; statsError.value = e.message } }),
    ]).finally(() => { if (requestVersion === version) { loading.value = false; pending = null } })
    return pending
  }
  const counts = computed(() => Object.fromEntries(['pending', 'approved', 'failed', 'deleted'].map((status) => [status, documents.value.filter((doc) => doc.status === status).length])))
  return { documents, stats, loading, loaded, error, statsError, counts, refresh, reset }
}
