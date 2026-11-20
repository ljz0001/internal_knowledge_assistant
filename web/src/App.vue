<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import Icon from './components/Icon.vue'
import DashboardView from './views/DashboardView.vue'
import ChatView from './views/ChatView.vue'
import KnowledgeView from './views/KnowledgeView.vue'
import BusinessView from './views/BusinessView.vue'
import SettingsView from './views/SettingsView.vue'
import { useKnowledge } from './composables/useKnowledge.js'
import { api } from './api/client.js'

const navigation = [
  { id: 'dashboard', label: '工作台', icon: 'grid', en: 'Overview' },
  { id: 'chat', label: '智能问答', icon: 'chat', en: 'AI Assistant' },
  { id: 'knowledge', label: '企业知识库', icon: 'book', en: 'Knowledge Base' },
  { id: 'business', label: '办公数据', icon: 'database', en: 'Workspace Data' },
  { id: 'settings', label: '连接与设置', icon: 'settings', en: 'Settings' },
]
const validPage = () => navigation.some((item) => item.id === location.hash.slice(1)) ? location.hash.slice(1) : 'dashboard'
const page = ref(validPage())
const current = computed(() => navigation.find((item) => item.id === page.value))
const menuOpen = ref(false)
const service = ref('checking')
const serviceError = ref('')
const initialQuery = ref('')
const toast = ref(null)
const knowledge = useKnowledge()
let toastTimer
let connectionVersion = 0
function notify(message, type = 'success') { toast.value = { message, type }; clearTimeout(toastTimer); toastTimer = setTimeout(() => { toast.value = null }, 6000) }
function navigate(id) { location.hash = id; page.value = id; menuOpen.value = false }
function syncHash() { page.value = validPage(); menuOpen.value = false }
function ask(text) { initialQuery.value = text; navigate('chat') }
async function reconnect() {
  const version = ++connectionVersion
  service.value = 'checking'; serviceError.value = ''
  try { await api.health(); if (version === connectionVersion) service.value = 'online' }
  catch (e) { if (version === connectionVersion) { service.value = 'offline'; serviceError.value = e.message } }
}
function reloadConnection() { reconnect(); knowledge.reset(); knowledge.refresh() }
function focusContent() { document.getElementById('main-content')?.focus() }
onMounted(() => { window.addEventListener('hashchange', syncHash); reconnect(); knowledge.refresh() })
onUnmounted(() => { window.removeEventListener('hashchange', syncHash); clearTimeout(toastTimer) })
</script>
<template>
  <a class="skip-link" href="#main-content" @click.prevent="focusContent">跳转到主要内容</a>
  <div class="app-shell"><div v-if="menuOpen" class="sidebar-backdrop" @click="menuOpen = false"></div><aside class="sidebar" :class="{ open: menuOpen }"><a class="brand" href="#dashboard" @click.prevent="navigate('dashboard')"><span class="brand-symbol"><Icon name="book" :size="24" /></span><span><strong>知序<span class="brand-en"> ZHIXU</span></strong><small>企业知识助手</small></span></a><div class="workspace-label"><span class="workspace-avatar">企</span><div><strong>企业工作空间</strong><small>让知识流动起来</small></div><Icon name="chevron" :size="14" /></div><span class="nav-label">WORKSPACE</span><nav aria-label="主导航"><button v-for="item in navigation.slice(0, 4)" :key="item.id" :class="{ active: page === item.id }" :aria-current="page === item.id ? 'page' : undefined" @click="navigate(item.id)"><Icon :name="item.icon" :size="20" /><span>{{ item.label }}</span><span v-if="item.id === 'chat'" class="ai-label">AI</span><span v-if="item.id === 'knowledge' && knowledge.counts.value.pending" class="nav-count">{{ knowledge.counts.value.pending }}</span></button></nav><div class="sidebar-bottom"><div class="sidebar-tip"><span class="sidebar-tip-symbol"><Icon name="sparkles" :size="18" /></span><strong>知识连接，灵感发生</strong><p>让每一次提问，<br />都成为工作的下一步。</p></div><nav aria-label="系统设置"><button :class="{ active: page === 'settings' }" @click="navigate('settings')"><Icon name="settings" :size="19" /><span>连接与设置</span></button></nav><div class="workspace-footer"><span class="avatar">企</span><div><strong>本地工作空间</strong><small>企业知识助手 · v1.0</small></div><Icon name="shield" :size="16" /></div></div></aside>
    <div class="app-main"><header class="topbar"><div class="breadcrumb"><button class="icon-button mobile-only" aria-label="打开导航菜单" :aria-expanded="menuOpen" @click="menuOpen = !menuOpen"><Icon name="menu" /></button><Icon name="grid" :size="16" /><span>工作空间</span><Icon name="chevron" :size="12" /><strong>{{ current.label }}</strong></div><div class="topbar-actions"><button class="connection-button" :title="serviceError || '检查 API 连接'" @click="navigate('settings')"><span class="status-dot" :class="service"></span>{{ service === 'online' ? 'API 已连接' : service === 'checking' ? '检测连接中' : 'API 未连接' }}</button><span class="topbar-divider"></span><span class="avatar">企</span></div></header>
      <main id="main-content" tabindex="-1" class="main-content" :class="{ 'chat-page': page === 'chat' }"><DashboardView v-if="page === 'dashboard'" :knowledge="knowledge" :service="service" @navigate="navigate" @ask="ask" /><ChatView v-show="page === 'chat'" :initial-query="initialQuery" @consumed="initialQuery = ''" @notify="notify" /><KnowledgeView v-if="page === 'knowledge'" :knowledge="knowledge" @notify="notify" /><BusinessView v-if="page === 'business'" @notify="notify" /><SettingsView v-if="page === 'settings'" @notify="notify" @reconnect="reloadConnection" /></main>
    </div><Transition name="toast"><div v-if="toast" class="toast" :class="toast.type" role="status"><Icon :name="toast.type === 'success' ? 'check' : 'help'" :size="19" /><span>{{ toast.message }}</span><button class="icon-button" aria-label="关闭提示" @click="toast = null"><Icon name="close" :size="16" /></button></div></Transition>
  </div>
</template>
