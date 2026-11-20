<script setup>
import { computed, ref } from 'vue'
import Icon from '../components/Icon.vue'
import Modal from '../components/Modal.vue'
import { api } from '../api/client.js'
import { resources } from '../config/resources.js'
const emit = defineEmits(['notify'])
const resource = ref('employees')
const config = computed(() => resources[resource.value])
const rows = ref([])
const filters = ref({})
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const formError = ref('')
const queried = ref(false)
const page = ref(0)
const pageSize = 20
const editor = ref(null)
const deletion = ref(null)
const form = ref({})
const fields = computed(() => [...config.value.fields, ...(editor.value?.id != null ? config.value.editFields || [] : [])])
let requestId = 0
async function load(reset = false) {
  if (reset) page.value = 0
  const version = ++requestId
  const key = resource.value
  const params = Object.fromEntries(Object.entries(filters.value).filter(([, value]) => String(value).trim() !== ''))
  error.value = ''
  if (config.value.filters && !Object.keys(params).length) { error.value = '请至少填写一个查询条件'; return }
  if (key === 'employees') Object.assign(params, { skip: page.value * pageSize, limit: pageSize })
  loading.value = true
  try { const data = await api.records(key, params); if (version === requestId) { rows.value = Array.isArray(data) ? data : []; queried.value = true } }
  catch (e) { if (version === requestId) { error.value = e.message; rows.value = [] } }
  finally { if (version === requestId) loading.value = false }
}
function switchResource(key) {
  if (key === resource.value) return
  requestId++; loading.value = false; resource.value = key; rows.value = []; filters.value = {}; error.value = ''; page.value = 0; queried.value = false
  if (key === 'employees') load()
}
function edit(record) {
  editor.value = record || {}
  form.value = Object.fromEntries([...config.value.fields, ...(record ? config.value.editFields || [] : [])].map((field) => [field.key, record?.[field.key] ?? config.value.defaults?.[field.key] ?? '']))
  formError.value = ''
}
async function save() {
  if (saving.value) return
  const updating = editor.value.id != null
  const payload = {}
  for (const field of fields.value) {
    if (updating && config.value.immutable?.includes(field.key)) continue
    const value = typeof form.value[field.key] === 'string' ? form.value[field.key].trim() : form.value[field.key]
    if (field.required && (value === '' || value == null)) { formError.value = `请填写${field.label}`; return }
    payload[field.key] = field.type === 'number' ? Number(value) : value
  }
  if (resource.value === 'leaves' && payload.end_date < payload.start_date) { formError.value = '结束日期不能早于开始日期'; return }
  saving.value = true; formError.value = ''
  try { await api.saveRecord(resource.value, payload, editor.value.id); editor.value = null; emit('notify', updating ? '记录已更新' : '记录已新增'); if (queried.value || resource.value === 'employees') await load() }
  catch (e) { formError.value = e.message }
  finally { saving.value = false }
}
async function remove() {
  if (saving.value) return
  saving.value = true; formError.value = ''
  try { await api.deleteRecord(resource.value, deletion.value.id); deletion.value = null; emit('notify', '记录已删除'); if (page.value > 0 && rows.value.length === 1) page.value--; await load() }
  catch (e) { formError.value = e.message }
  finally { saving.value = false }
}
function deletePrompt(row) { formError.value = ''; deletion.value = row }
function paginate(delta) { page.value += delta; load() }
load()
</script>
<template>
  <div class="page"><div class="page-heading"><div><div class="eyebrow">WORKSPACE DATA</div><h1>办公数据</h1><p>人员与日常事务，清晰有序。</p></div><button class="button primary" :disabled="loading" @click="edit()"><Icon name="plus" :size="18" />新增记录</button></div>
    <div class="resource-tabs"><button v-for="(item, key) in resources" :key="key" :class="{ active: key === resource }" @click="switchResource(key)"><Icon :name="item.icon" :size="19" />{{ item.label }}</button></div>
    <section class="panel"><div class="section-heading"><div><h2>{{ config.label }}</h2><p>{{ config.hint }}</p></div><button class="icon-button" :disabled="loading" aria-label="刷新业务数据" @click="load()"><Icon name="refresh" :size="18" :class="{ spinning: loading }" /></button></div>
      <form v-if="config.filters" class="filter-form" @submit.prevent="load(true)"><label v-for="field in config.filters" :key="field.key">{{ field.label }}<input v-model="filters[field.key]" :type="field.type" :min="field.type === 'number' ? 1 : undefined" :step="field.type === 'number' ? 1 : undefined" :placeholder="`请输入${field.label}`" /></label><button class="button primary" :disabled="loading"><Icon name="search" :size="17" />查询</button></form>
      <div v-if="error" class="inline-error" role="alert">{{ error }}</div><div class="table-scroll"><table><thead><tr><th v-for="[key, label] in config.columns" :key="key">{{ label }}</th><th class="align-right">操作</th></tr></thead><tbody><tr v-for="row in rows" :key="row.id"><td v-for="[key] in config.columns" :key="key">{{ row[key] ?? '—' }}</td><td><div class="row-actions"><button class="text-button" @click="edit(row)"><Icon name="edit" :size="15" />编辑</button><button v-if="config.deletable" class="icon-button danger-text" aria-label="删除记录" @click="deletePrompt(row)"><Icon name="trash" :size="16" /></button></div></td></tr></tbody></table></div><div v-if="!rows.length" class="empty-state"><Icon :name="loading ? 'refresh' : config.icon" :size="34" :class="{ spinning: loading }" /><h3>{{ loading ? '正在查询…' : queried ? '没有匹配的记录' : config.filters ? '填写条件，开始查询' : '暂无数据' }}</h3><p>数据直接来自后端业务数据库。</p></div>
      <footer class="table-footer"><span>当前显示 {{ rows.length }} 条记录</span><div v-if="resource === 'employees'" class="inline"><button class="button small-button" :disabled="page === 0 || loading" @click="paginate(-1)">上一页</button><span>第 {{ page + 1 }} 页</span><button class="button small-button" :disabled="rows.length < pageSize || loading" @click="paginate(1)">下一页</button></div></footer>
    </section><p class="muted small section-note"><Icon name="shield" :size="15" />当前为本地办公数据管理入口，操作会直接写入业务数据库。</p>
    <Modal v-if="editor" :title="`${editor.id != null ? '编辑' : '新增'} · ${config.label}`" :busy="saving" @close="editor = null"><form @submit.prevent="save"><div class="form-grid"><label v-for="field in fields" :key="field.key">{{ field.label }}<span v-if="field.required" class="required">*</span><input v-model="form[field.key]" :type="field.type" :required="field.required" :disabled="saving || (editor.id != null && config.immutable?.includes(field.key))" :min="field.type === 'number' ? 1 : undefined" :step="field.type === 'time' ? 1 : field.type === 'number' ? 1 : undefined" :maxlength="field.key === 'reason' || field.key === 'remark' ? 500 : 100" /></label></div><div v-if="formError" class="inline-error" role="alert">{{ formError }}</div><footer class="modal-footer"><button type="button" class="button" :disabled="saving" @click="editor = null">取消</button><button class="button primary" :disabled="saving">{{ saving ? '保存中…' : '保存记录' }}</button></footer></form></Modal>
    <Modal v-if="deletion" title="确认删除记录" :busy="saving" @close="deletion = null"><p class="modal-description">将从数据库删除记录 #{{ deletion.id }}（{{ deletion.emp_name || deletion.name }}），此操作无法在页面中撤回。</p><div v-if="formError" class="inline-error" role="alert">{{ formError }}</div><footer class="modal-footer"><button class="button" :disabled="saving" @click="deletion = null">取消</button><button class="button danger" :disabled="saving" @click="remove">{{ saving ? '删除中…' : '确认删除' }}</button></footer></Modal>
  </div>
</template>
