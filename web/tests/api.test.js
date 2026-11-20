import test, { afterEach } from 'node:test'
import assert from 'node:assert/strict'
import { api, request, validateApiBase } from '../src/api/client.js'

const originalFetch = globalThis.fetch
afterEach(() => { globalThis.fetch = originalFetch })
const jsonResponse = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })

test('解包统一响应，保留部分失败数据供页面逐条展示', async () => {
  const data = { uploaded: [{ id: 1 }], failed: [{ filename: '重复.md', error: '文件重复' }] }
  globalThis.fetch = async () => jsonResponse({ code: 0, msg: 'success', data }, 201)
  assert.deepEqual(await request('/rag/uploads'), data)
})
test('HTTP 200 中的业务错误仍抛出异常', async () => {
  globalThis.fetch = async () => jsonResponse({ code: 5000, msg: '模型服务异常', data: null })
  await assert.rejects(request('/chat/'), /模型服务异常/)
})
test('把 FastAPI 422 校验详情转为可读消息', async () => {
  globalThis.fetch = async () => jsonResponse({ detail: [{ loc: ['body', 'emp_id'], msg: 'Input should be a valid integer' }] }, 422)
  await assert.rejects(request('/db/attendance'), /emp_id：Input should be a valid integer/)
})
test('非 JSON 响应提醒检查代理，网络错误给出连接提示', async () => {
  globalThis.fetch = async () => new Response('<html>fallback</html>')
  await assert.rejects(request('/'), /接口未返回 JSON/)
  globalThis.fetch = async () => { throw new TypeError('Failed to fetch') }
  await assert.rejects(request('/'), /无法连接后端/)
})
test('超时中断请求，并提示后台操作可能继续', async () => {
  globalThis.fetch = async (_url, options) => new Promise((_resolve, reject) => options.signal.addEventListener('abort', () => reject(new DOMException('timeout', 'AbortError'))))
  await assert.rejects(request('/slow', { timeout: 10 }), /请求超时；后台操作可能仍在执行/)
})
test('对话提交 query 和独立 session_id；健康检查不解包', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/chat/')
    assert.equal(options.method, 'POST')
    assert.deepEqual(JSON.parse(options.body), { query: '年假流程', session_id: 'session-test' })
    return jsonResponse({ code: 0, data: { answer: '测试回答' } })
  }
  assert.equal((await api.chat('年假流程', 'session-test')).answer, '测试回答')
  globalThis.fetch = async () => jsonResponse({ version: '1.0.0' })
  assert.deepEqual(await api.health('/api'), { version: '1.0.0' })
})
test('上传用重复 files 字段且不手动覆盖 multipart boundary', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/rag/uploads')
    assert.equal(options.headers['Content-Type'], undefined)
    assert.equal(options.body.getAll('files').length, 2)
    return jsonResponse({ code: 0, data: { uploaded: [], failed: [] } })
  }
  await api.upload([new File(['first'], '制度.txt'), new File(['second'], '流程.md')])
})
test('校验 API 地址，拒绝脚本、账号、查询参数与协议相对地址', () => {
  assert.equal(validateApiBase(' /api/ '), '/api')
  assert.equal(validateApiBase('http://localhost:8000/'), 'http://localhost:8000')
  for (const value of ['javascript:alert(1)', '//example.com', 'https://user:pass@example.com', 'https://example.com?a=1', '']) assert.throws(() => validateApiBase(value))
})
