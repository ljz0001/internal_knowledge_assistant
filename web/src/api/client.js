import { readStorage } from '../utils/storage.js'

const defaultBase = import.meta.env?.VITE_API_BASE_URL || '/api'
export function getApiBase() { return readStorage('zhixu-api-base', defaultBase) || defaultBase }
export function validateApiBase(value) {
  const base = value.trim().replace(/\/+$/, '')
  if (/^\/(?!\/)[\w/.-]+$/.test(base)) return base
  try {
    const url = new URL(base)
    if (['http:', 'https:'].includes(url.protocol) && !url.username && !url.password && !url.search && !url.hash) return base
  } catch { /* 统一给出可读提示 */ }
  throw new Error('请输入 /api 这样的路径，或不含账号、查询参数的 http(s) 地址')
}
export function errorMessage(body, fallback) {
  if (Array.isArray(body?.detail)) return body.detail.map((item) => `${item.loc?.slice(1).join('.') || '参数'}：${item.msg}`).join('；')
  return (typeof body?.detail === 'string' && body.detail) || body?.msg || fallback
}
export async function request(path, { method = 'GET', body, timeout = 120000, base = getApiBase(), raw = false } = {}) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeout)
  const multipart = typeof FormData !== 'undefined' && body instanceof FormData
  try {
    const response = await fetch(`${base.replace(/\/+$/, '')}${path}`, {
      method, signal: controller.signal,
      headers: body && !multipart ? { 'Content-Type': 'application/json' } : {},
      body: body ? (multipart ? body : JSON.stringify(body)) : undefined,
    })
    const text = await response.text()
    let result
    try { result = text ? JSON.parse(text) : {} } catch { throw new Error('接口未返回 JSON，请检查服务地址与代理配置') }
    if (!response.ok) throw new Error(errorMessage(result, [502, 503, 504].includes(response.status) ? `后端服务暂不可用（HTTP ${response.status}），请确认后端已启动` : `请求失败（HTTP ${response.status}）`))
    if (!raw && typeof result.code === 'number' && result.code !== 0) throw new Error(errorMessage(result, '业务处理失败'))
    return raw ? result : result.data
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('请求超时；后台操作可能仍在执行，请刷新确认结果后再重试')
    if (error instanceof TypeError) throw new Error('无法连接后端，请检查服务是否启动及接口地址是否正确')
    throw error
  } finally { clearTimeout(timer) }
}
export const api = {
  health: (base) => request('/', { raw: true, timeout: 10000, base }),
  mode: () => request('/agent/mode', { timeout: 10000 }),
  chat: (query, session_id) => request('/chat/', { method: 'POST', body: { query, session_id } }),
  search: (query) => request('/rag/search', { method: 'POST', body: { query } }),
  documents: () => request('/rag/uploads'),
  stats: () => request('/rag/stats'),
  upload: (files) => {
    const body = new FormData()
    files.forEach((file) => body.append('files', file))
    return request('/rag/uploads', { method: 'POST', body })
  },
  approve: (document_ids) => request('/rag/uploads/approve-batch', { method: 'POST', body: { document_ids } }),
  deleteDocuments: (document_ids) => request('/rag/uploads/delete-batch', { method: 'POST', body: { document_ids } }),
  records: (resource, params) => request(`/db/${resource}?${new URLSearchParams(params)}`),
  saveRecord: (resource, body, id) => request(`/db/${resource}${id == null ? '' : `/${id}`}`, { method: id == null ? 'POST' : 'PATCH', body }),
  deleteRecord: (resource, id) => request(`/db/${resource}/${id}`, { method: 'DELETE' }),
}
