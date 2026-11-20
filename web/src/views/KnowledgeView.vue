<script setup>
import { computed, ref, watch } from 'vue'
import { api } from '../api/client.js'
import Icon from '../components/Icon.vue'
import Modal from '../components/Modal.vue'
import { formatDate, formatSize } from '../utils/storage.js'
const props = defineProps({ knowledge: Object })
const emit = defineEmits(['notify'])
const filter = ref('all')
const search = ref('')
const selected = ref([])
const busy = ref(false)
const uploadOpen = ref(false)
const dragOver = ref(false)
const chosen = ref([])
const fileInput = ref(null)
const fileErrors = ref([])
const results = ref([])
const confirm = ref(null)
const detail = ref(null)
const labels = { pending: '待审核', approved: '已入库', failed: '入库失败', deleted: '已删除' }
const rows = computed(() => props.knowledge.documents.value.filter((doc) => (filter.value === 'all' ? doc.status !== 'deleted' : doc.status === filter.value) && doc.original_name.toLowerCase().includes(search.value.toLowerCase())))
const eligible = computed(() => rows.value.filter((doc) => ['pending', 'failed'].includes(doc.status)))
const allSelected = computed(() => eligible.value.length > 0 && eligible.value.every((doc) => selected.value.includes(doc.id)))
watch([filter, search, () => props.knowledge.documents.value], () => { selected.value = [] })
function toggleAll(event) { selected.value = event.target.checked ? eligible.value.map((doc) => doc.id) : [] }
function choose(files) {
  fileErrors.value = []
  for (const file of Array.from(files || [])) {
    if (!/\.(txt|md|pdf)$/i.test(file.name)) fileErrors.value.push(`${file.name}：仅支持 TXT、MD、PDF`)
    else if (!file.size || file.size > 10 * 1024 * 1024) fileErrors.value.push(`${file.name}：文件不能为空且不能超过 10 MB`)
    else if (!chosen.value.some((item) => item.name === file.name && item.size === file.size && item.lastModified === file.lastModified)) chosen.value.push(file)
  }
  if (fileInput.value) fileInput.value.value = ''
}
function drop(event) { dragOver.value = false; if (!busy.value) choose(event.dataTransfer.files) }
async function upload() {
  if (!chosen.value.length || busy.value) return
  busy.value = true; results.value = []
  try {
    const result = await api.upload(chosen.value)
    results.value = (result.failed || []).map((item) => `${item.filename}：${item.error}`)
    chosen.value = []
    emit('notify', `已上传 ${result.uploaded?.length || 0} 份文件，等待审核${results.value.length ? `；${results.value.length} 份失败` : ''}`, results.value.length ? 'warning' : 'success')
    await props.knowledge.refresh()
    if (!results.value.length) uploadOpen.value = false
  } catch (e) { results.value = [e.message] }
  finally { busy.value = false }
}
function requestAction(action, ids) {
  if (!ids.length || busy.value) return
  confirm.value = { action, ids: [...ids] }
}
async function perform() {
  if (!confirm.value || busy.value) return
  const { action, ids } = confirm.value
  busy.value = true; results.value = []
  try {
    const result = await (action === 'approve' ? api.approve(ids) : api.deleteDocuments(ids))
    const success = result[action === 'approve' ? 'approved' : 'deleted'] || []
    results.value = (result.failed || []).map((item) => `文件 #${item.id}：${item.error}`)
    emit('notify', `${action === 'approve' ? '入库' : '删除'}成功 ${success.length} 份${results.value.length ? `，失败 ${results.value.length} 份` : ''}`, results.value.length ? 'warning' : 'success')
    await props.knowledge.refresh()
  } catch (e) { results.value = [e.message] }
  finally { busy.value = false; confirm.value = null }
}
function openUpload() { chosen.value = []; fileErrors.value = []; results.value = []; uploadOpen.value = true }
</script>
<template>
  <div class="page">
    <div class="page-heading"><div><div class="eyebrow">ENTERPRISE KNOWLEDGE</div><h1>企业知识库</h1><p>汇聚团队经验，让每一份知识都有价值。</p></div><button class="button primary" :disabled="busy" @click="openUpload"><Icon name="upload" :size="18" />上传文档</button></div>
    <div class="notice-strip"><span class="notice-icon"><Icon name="shield" /></span><div><strong>先审核，再共享</strong><p>上传的文件先进入待审核列表，审核入库后才能被智能助手检索。</p></div><span class="small muted">TXT / MD / PDF · 单个文件 ≤ 10 MB</span></div>
    <div v-if="knowledge.statsError.value" class="inline-error" role="alert">知识片段统计不可用：{{ knowledge.statsError.value }}</div>
    <div v-if="results.length && !uploadOpen" class="inline-error" role="alert"><strong>以下操作未完成</strong><p v-for="item in results" :key="item">{{ item }}</p><button class="text-button" @click="results = []">收起</button></div>
    <section class="panel document-panel"><div class="document-toolbar"><div class="tabs"><button v-for="(label, key) in { all: '全部文档', pending: '待审核', approved: '已入库', failed: '入库失败', deleted: '已删除' }" :key="key" :class="{ active: filter === key }" @click="filter = key">{{ label }}<span v-if="key !== 'all'">{{ knowledge.loaded.value ? knowledge.counts.value[key] : '—' }}</span></button></div><div class="inline"><label class="search-field"><Icon name="search" :size="17" /><input v-model="search" placeholder="搜索文档名称" aria-label="搜索文档名称" /></label><button class="icon-button" :disabled="knowledge.loading.value || busy" aria-label="刷新文档" @click="knowledge.refresh"><Icon name="refresh" :class="{ spinning: knowledge.loading.value }" :size="18" /></button></div></div>
      <div v-if="selected.length" class="selection-bar"><span>已选择 {{ selected.length }} 份文档</span><button class="text-button" :disabled="busy" @click="requestAction('approve', selected)"><Icon name="check" :size="16" />批量入库</button><button class="text-button danger-text" :disabled="busy" @click="requestAction('delete', selected)"><Icon name="trash" :size="16" />批量删除</button><button class="text-button" :disabled="busy" @click="selected = []">取消选择</button></div>
      <div v-if="knowledge.error.value" class="inline-error" role="alert">{{ knowledge.error.value }}<button class="text-button" @click="knowledge.refresh">重新加载</button></div>
      <div class="table-scroll"><table><thead><tr><th class="checkbox-cell"><input type="checkbox" aria-label="选择所有可操作文档" :checked="allSelected" :disabled="!eligible.length || busy" @change="toggleAll" /></th><th>文档名称</th><th>文件大小</th><th>上传时间</th><th>状态</th><th class="align-right">操作</th></tr></thead><tbody><tr v-for="doc in rows" :key="doc.id"><td><input v-model="selected" type="checkbox" :value="doc.id" :aria-label="`选择 ${doc.original_name}`" :disabled="busy || !['pending', 'failed'].includes(doc.status)" /></td><td><button class="file-name" @click="detail = doc"><span class="file-icon" :class="doc.file_type?.replace('.', '')"><Icon name="file" :size="19" /></span><span><strong>{{ doc.original_name }}</strong><small>{{ doc.file_type?.replace('.', '').toUpperCase() }} 文档 · #{{ doc.id }}</small></span></button></td><td class="muted">{{ formatSize(doc.file_size) }}</td><td class="muted nowrap">{{ formatDate(doc.create_time) }}</td><td><span class="badge" :class="doc.status">{{ labels[doc.status] }}</span></td><td><div class="row-actions"><button v-if="['pending', 'failed'].includes(doc.status)" class="text-button" :disabled="busy" @click="requestAction('approve', [doc.id])">{{ doc.status === 'failed' ? '重试入库' : '审核入库' }}</button><button class="text-button" @click="detail = doc">详情</button><button v-if="['pending', 'failed'].includes(doc.status)" class="icon-button danger-text" aria-label="删除文档" :disabled="busy" @click="requestAction('delete', [doc.id])"><Icon name="trash" :size="16" /></button></div></td></tr></tbody></table></div>
      <div v-if="!rows.length" class="empty-state"><Icon :name="knowledge.loading.value ? 'refresh' : 'book'" :size="36" :class="{ spinning: knowledge.loading.value }" /><h3>{{ knowledge.loading.value ? '正在加载知识库…' : '这里还没有文档' }}</h3><p>{{ search ? '试试其他关键词，或切换文档状态。' : '上传制度、流程或工作手册，开始积累团队知识。' }}</p><button v-if="!search && filter === 'all'" class="button" @click="openUpload">上传第一份文档</button></div>
      <footer class="table-footer"><span>{{ knowledge.loaded.value ? `当前显示 ${rows.length} 份文档` : '尚未获取文档数据' }}</span><span>知识片段 {{ knowledge.stats.value?.vector_count ?? '—' }} 条 · 待审核 / 入库失败文档支持批量操作</span></footer>
    </section>
    <div class="knowledge-flow"><div><span>01</span><strong>上传文档</strong><p>支持 TXT、Markdown 和 PDF</p></div><Icon name="arrow" /><div><span>02</span><strong>人工审核</strong><p>确认资料适合进入知识库</p></div><Icon name="arrow" /><div><span>03</span><strong>知识入库</strong><p>文档切分、向量化并开放检索</p></div></div>
    <Modal v-if="uploadOpen" title="上传企业文档" :busy="busy" @close="uploadOpen = false"><p class="muted modal-description">选择需要共享的资料。上传成功后，还需审核才能入库。</p><div class="drop-zone" :class="{ dragging: dragOver }" @dragover.prevent="dragOver = true" @dragleave.prevent="dragOver = false" @drop.prevent="drop"><span class="quick-icon purple"><Icon name="upload" :size="25" /></span><strong>拖放文件到这里，或点击选择</strong><p>TXT、MD、PDF · 单个文件最大 10 MB</p><button class="button" :disabled="busy" @click="fileInput.click()">选择文件</button><input ref="fileInput" class="sr-only" type="file" accept=".txt,.md,.pdf" multiple :disabled="busy" aria-label="选择上传文件" @change="choose($event.target.files)" /></div><div class="upload-files"><div v-for="(file, index) in chosen" :key="`${file.name}-${file.lastModified}`" class="upload-file"><Icon name="file" :size="18" /><span>{{ file.name }}<small>{{ formatSize(file.size) }}</small></span><button class="icon-button" :disabled="busy" aria-label="移除文件" @click="chosen.splice(index, 1)"><Icon name="close" :size="16" /></button></div></div><div v-if="fileErrors.length || results.length" class="inline-error" role="alert"><p v-for="item in [...fileErrors, ...results]" :key="item">{{ item }}</p></div><footer class="modal-footer"><button class="button" :disabled="busy" @click="uploadOpen = false">取消</button><button class="button primary" :disabled="!chosen.length || busy" @click="upload">{{ busy ? '上传中…' : `上传${chosen.length ? ` ${chosen.length} 份文档` : ''}` }}</button></footer></Modal>
    <Modal v-if="confirm" :title="confirm.action === 'approve' ? '确认审核入库' : '确认删除文档'" :busy="busy" @close="confirm = null"><p class="modal-description">{{ confirm.action === 'approve' ? `将 ${confirm.ids.length} 份文档写入知识库。请确认资料内容准确且适合共享，入库过程可能需要一段时间。` : `将删除 ${confirm.ids.length} 份待审核或入库失败的原始上传文件，此操作无法在页面中撤回。` }}</p><footer class="modal-footer"><button class="button" :disabled="busy" @click="confirm = null">取消</button><button class="button" :class="confirm.action === 'approve' ? 'primary' : 'danger'" :disabled="busy" @click="perform">{{ busy ? '处理中…' : '确认操作' }}</button></footer></Modal>
    <Modal v-if="detail" title="文档详情" @close="detail = null"><dl class="detail-list"><dt>文件名称</dt><dd>{{ detail.original_name }}</dd><dt>文档 ID</dt><dd>{{ detail.id }}</dd><dt>文件大小</dt><dd>{{ formatSize(detail.file_size) }}</dd><dt>状态</dt><dd><span class="badge" :class="detail.status">{{ labels[detail.status] }}</span></dd><dt>上传时间</dt><dd>{{ formatDate(detail.create_time) }}</dd><dt>审核时间</dt><dd>{{ formatDate(detail.approved_at) }}</dd><dt>最后更新</dt><dd>{{ formatDate(detail.update_time) }}</dd></dl><div v-if="detail.error_message" class="inline-error">{{ detail.error_message }}</div><p class="muted small">当前接口提供文档元数据，暂不提供原文预览或下载。</p></Modal>
  </div>
</template>
