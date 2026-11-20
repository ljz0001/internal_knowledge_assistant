// 浏览器禁用存储或本地数据损坏时，页面仍可使用。
export function readStorage(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback } catch { return fallback }
}
export function writeStorage(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); return true } catch { return false }
}
export const uid = () => globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`
export const formatDate = (value) => value ? String(value).replace('T', ' ').slice(0, 16) : '—'
export function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  return bytes < 1048576 ? `${(bytes / 1024).toFixed(1)} KB` : `${(bytes / 1048576).toFixed(1)} MB`
}
