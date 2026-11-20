<script setup>
import { computed, ref } from 'vue'
import Icon from '../components/Icon.vue'
import { formatDate, formatSize } from '../utils/storage.js'
const props = defineProps({ knowledge: Object, service: String })
const emit = defineEmits(['navigate', 'ask'])
const query = ref('')
const recent = computed(() => [...props.knowledge.documents.value].filter((doc) => doc.status !== 'deleted').sort((a, b) => b.id - a.id).slice(0, 4))
const suggestions = ['公司的年假申请流程是什么？', '如何查询员工的考勤记录？', '试用期员工有哪些福利？']
const statusLabels = { pending: '待审核', approved: '已入库', failed: '入库失败' }
function ask() { if (query.value.trim()) emit('ask', query.value.trim()) }
</script>
<template>
  <div class="page dashboard">
    <div class="page-heading"><div><div class="eyebrow">YOUR KNOWLEDGE, CONNECTED</div><h1>让知识，成为工作的助力<span class="heading-dot">。</span></h1><p>从一个问题开始，找到你需要的答案。</p></div><span class="date-label">企业知识工作台</span></div>
    <section class="hero-panel">
      <div class="hero-content"><span class="hero-tag"><Icon name="sparkles" :size="14" /> 你的企业智能伙伴</span><h2>每一个好问题，<br />都值得一个可靠的答案。</h2><p>连接企业知识与办公数据，让信息触手可及。</p>
        <form class="hero-search" @submit.prevent="ask"><Icon name="search" /><input v-model="query" aria-label="向智能助手提问" placeholder="问问知序，例如：年假应该如何申请？" maxlength="2000" /><button class="icon-button primary" aria-label="发送问题" :disabled="!query.trim()"><Icon name="arrow" /></button></form>
        <div class="hero-topics"><span>试着问问</span><button v-for="text in suggestions.slice(0, 2)" :key="text" @click="emit('ask', text)">{{ text }}<Icon name="chevron" :size="12" /></button></div>
      </div>
      <div class="knowledge-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="art-glow"></div><div class="floating-label label-top"><span class="tiny-dot"></span> KNOWLEDGE CONNECTED</div><div class="art-book"><div class="book-page left-page"><i></i><i></i><i></i><i></i></div><div class="book-page right-page"><Icon name="sparkles" :size="34" /><i></i><i></i></div></div><div class="art-star star-one">✦</div><div class="art-star star-two">✧</div><div class="floating-label label-bottom"><Icon name="check" :size="15" /> 让每一份知识都有价值</div></div>
    </section>
    <div class="metrics-grid">
      <button class="metric-card" @click="emit('navigate', 'knowledge')"><span class="metric-icon purple"><Icon name="book" /></span><div><span>已入库文档</span><strong>{{ knowledge.loaded.value ? knowledge.counts.value.approved : '—' }}<small>份</small></strong></div><Icon name="chevron" :size="15" /></button>
      <button class="metric-card" @click="emit('navigate', 'knowledge')"><span class="metric-icon amber"><Icon name="clock" /></span><div><span>等待审核</span><strong>{{ knowledge.loaded.value ? knowledge.counts.value.pending : '—' }}<small>份</small></strong></div><Icon name="chevron" :size="15" /></button>
      <button class="metric-card" @click="emit('navigate', 'knowledge')"><span class="metric-icon blue"><Icon name="database" /></span><div><span>知识片段</span><strong>{{ knowledge.stats.value?.vector_count ?? '—' }}<small>条</small></strong></div><Icon name="chevron" :size="15" /></button>
      <button class="metric-card" @click="emit('navigate', 'settings')"><span class="metric-icon green"><Icon name="shield" /></span><div><span>API 服务连接</span><strong class="service-text">{{ service === 'online' ? '已连接' : service === 'checking' ? '检测中' : '未连接' }}</strong></div><span class="status-dot" :class="service"></span></button>
    </div>
    <section><div class="section-heading"><div><h2>开启高效工作</h2><p>把繁琐留给工具，把时间留给思考。</p></div></div><div class="quick-grid">
      <button class="quick-card" @click="emit('navigate', 'chat')"><span class="quick-icon purple"><Icon name="chat" :size="25" /></span><h3>智能问答<Icon name="arrow" :size="18" /></h3><p>制度不清楚？流程不熟悉？<br />让智能助手为你解答。</p><span class="text-link">开始对话</span></button>
      <button class="quick-card" @click="emit('navigate', 'knowledge')"><span class="quick-icon blue"><Icon name="book" :size="25" /></span><h3>企业知识库<Icon name="arrow" :size="18" /></h3><p>上传、审核与管理企业文档，<br />让团队经验持续沉淀。</p><span class="text-link">管理知识</span></button>
      <button class="quick-card" @click="emit('navigate', 'business')"><span class="quick-icon green"><Icon name="users" :size="25" /></span><h3>办公数据<Icon name="arrow" :size="18" /></h3><p>员工、考勤、请假与通讯录，<br />在一个地方清晰掌握。</p><span class="text-link">查看数据</span></button>
    </div></section>
    <div class="dashboard-bottom"><section class="panel recent-panel"><div class="section-heading"><h2>最近上传</h2><button class="text-button" @click="emit('navigate', 'knowledge')">查看全部 <Icon name="arrow" :size="15" /></button></div>
      <div v-if="knowledge.error.value" class="inline-error" role="alert">{{ knowledge.error.value }}<button class="text-button" @click="knowledge.refresh">重试</button></div>
      <div v-else-if="knowledge.loading.value && !knowledge.loaded.value" class="empty-state compact">正在读取文档…</div>
      <div v-else-if="!recent.length" class="empty-state compact"><Icon name="file" :size="30" /><p>知识，从第一份文档开始</p><button class="text-button" @click="emit('navigate', 'knowledge')">上传企业文档 <Icon name="arrow" :size="14" /></button></div>
      <div v-for="doc in recent" :key="doc.id" class="recent-row"><span class="file-icon" :class="doc.file_type?.replace('.', '')"><Icon name="file" /></span><div><strong>{{ doc.original_name }}</strong><small>{{ formatSize(doc.file_size) }} · {{ formatDate(doc.create_time) }}</small></div><span class="badge" :class="doc.status">{{ statusLabels[doc.status] }}</span></div>
      <p v-if="knowledge.statsError.value" class="muted small">知识片段统计暂不可用，可前往知识库重试。</p>
    </section><aside class="tip-panel"><span class="eyebrow">A LITTLE TIP</span><div class="tip-icon"><Icon name="sparkles" :size="25" /></div><h2>提问更具体，<br />答案更有帮助。</h2><p>试着在问题中加上部门、时间或业务背景，让助手更好地理解你的需求。</p><button class="text-button" @click="emit('ask', '请介绍一下公司的请假流程，以及需要准备哪些材料？')">试一试 <Icon name="arrow" :size="16" /></button></aside></div>
    <footer class="page-footer"><span>知序 · 连接知识，简化工作</span><span>由企业知识库与智能助手提供支持</span></footer>
  </div>
</template>
