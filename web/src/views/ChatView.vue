<script setup>
import { computed, nextTick, onUnmounted, ref, watch } from 'vue'
import { api } from '../api/client.js'
import Icon from '../components/Icon.vue'
import { readStorage, uid, writeStorage } from '../utils/storage.js'
const props = defineProps({ initialQuery: String })
const emit = defineEmits(['consumed', 'notify'])
const stored = readStorage('zhixu-conversations', [])
const sessions = ref(Array.isArray(stored) ? stored.filter((s) => s && typeof s.id === 'string' && Array.isArray(s.messages)).slice(0, 20) : [])
const activeId = ref(sessions.value[0]?.id || '')
const active = computed(() => sessions.value.find((s) => s.id === activeId.value))
const draft = ref('')
const mode = ref('agent')
const sending = ref(false)
const transcript = ref(null)
const error = ref('')
const historyOpen = ref(false)
let mounted = true
onUnmounted(() => { mounted = false })
watch(sessions, (value) => writeStorage('zhixu-conversations', value.slice(0, 20)), { deep: true })
function newChat() {
  if (sending.value) return
  const session = { id: uid(), title: '新的对话', messages: [] }
  sessions.value.unshift(session)
  sessions.value = sessions.value.slice(0, 20)
  activeId.value = session.id; error.value = ''; draft.value = ''; historyOpen.value = false
}
if (!active.value) newChat()
function selectSession(id) { activeId.value = id; error.value = ''; draft.value = ''; historyOpen.value = false; scrollBottom() }
async function scrollBottom() { await nextTick(); if (mounted) transcript.value?.scrollTo({ top: transcript.value.scrollHeight, behavior: 'smooth' }) }
async function send(text = draft.value) {
  const query = text.trim()
  if (!query || sending.value) return
  if (!active.value) newChat()
  const target = active.value
  const requestMode = mode.value
  target.messages.push({ id: uid(), role: 'user', content: query })
  if (target.title === '新的对话') target.title = query.slice(0, 22)
  draft.value = ''; sending.value = true; error.value = ''; scrollBottom()
  try {
    const result = requestMode === 'agent' ? await api.chat(query, target.id) : await api.search(query)
    target.messages.push({ id: uid(), role: 'assistant', content: typeof result?.answer === 'string' ? result.answer : JSON.stringify(result?.answer ?? result ?? '接口没有返回回答'), steps: result?.steps || [], mode: requestMode })
  } catch (e) { error.value = e.message; draft.value = query }
  finally { sending.value = false; scrollBottom() }
}
function removeSession(id) {
  if (sending.value) return
  sessions.value = sessions.value.filter((s) => s.id !== id)
  if (id === activeId.value) activeId.value = sessions.value[0]?.id || ''
  if (!active.value) newChat()
}
async function copy(text) {
  try { await navigator.clipboard.writeText(text); emit('notify', '回答已复制') } catch { emit('notify', '复制失败，请手动选择文字复制', 'error') }
}
function onKeydown(event) { if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) { event.preventDefault(); send() } }
watch(() => props.initialQuery, (value) => { if (value) { draft.value = value; emit('consumed') } }, { immediate: true })
const suggestions = [
  { icon: 'book', title: '了解公司制度', text: '公司的年假申请流程是什么？' },
  { icon: 'users', title: '查找办公信息', text: '如何查询员工的考勤记录？' },
  { icon: 'shield', title: '熟悉工作流程', text: '入职需要准备哪些材料？' },
]
</script>
<template>
  <div class="chat-layout">
    <aside class="chat-history" :class="{ open: historyOpen }"><button class="button primary full" :disabled="sending" @click="newChat"><Icon name="plus" :size="18" />新建对话</button><div class="history-label">最近对话 <small>{{ sessions.length }}/20</small></div><div class="session-list"><div v-for="session in sessions" :key="session.id" class="session-item" :class="{ active: activeId === session.id }"><button :disabled="sending" @click="selectSession(session.id)"><Icon name="chat" :size="16" /><span>{{ session.title }}</span></button><button class="icon-button" :disabled="sending" aria-label="删除本地对话记录" @click="removeSession(session.id)"><Icon name="trash" :size="14" /></button></div></div><p class="history-note"><Icon name="shield" :size="16" />最近 20 个会话保存在当前浏览器。请勿在共享设备中保留敏感信息。</p></aside>
    <section class="chat-main"><header class="chat-header"><div class="inline"><button class="icon-button mobile-only" aria-label="展开对话历史" @click="historyOpen = !historyOpen"><Icon name="menu" /></button><div><h1>智能问答</h1><p>企业知识与办公信息，随问随答</p></div></div><div class="segmented"><button :class="{ active: mode === 'agent' }" :disabled="sending" @click="mode = 'agent'">智能助手</button><button :class="{ active: mode === 'rag' }" :disabled="sending" @click="mode = 'rag'">知识库检索</button></div></header>
      <div ref="transcript" class="transcript" aria-live="polite" aria-busy="sending">
        <div v-if="!active?.messages.length" class="chat-welcome"><span class="welcome-logo"><Icon name="sparkles" :size="34" /></span><span class="eyebrow">MEET YOUR KNOWLEDGE PARTNER</span><h2>你好，有什么可以帮你？</h2><p>{{ mode === 'agent' ? '我会结合企业知识与办公数据，帮助你找到答案。' : '仅检索企业知识库，每次检索独立进行。' }}</p><div class="prompt-grid"><button v-for="item in suggestions" :key="item.title" class="prompt-card" @click="draft = item.text"><Icon :name="item.icon" /><strong>{{ item.title }}</strong><span>{{ item.text }}</span><Icon name="arrow" :size="16" /></button></div></div>
        <div v-for="message in active?.messages" :key="message.id" class="message" :class="message.role"><span class="message-avatar"><Icon v-if="message.role === 'assistant'" name="sparkles" :size="18" /><span v-else>我</span></span><div class="message-body"><span class="message-author">{{ message.role === 'user' ? '你' : message.mode === 'rag' ? '知序 · 知识库检索' : '知序助手' }}</span><div class="message-text">{{ message.content }}</div><details v-if="message.steps?.length" class="tool-steps"><summary>查看工具调用记录</summary><pre>{{ message.steps.join('\n') }}</pre></details><button v-if="message.role === 'assistant'" class="copy-button" @click="copy(message.content)"><Icon name="copy" :size="14" />复制回答</button></div></div>
        <div v-if="sending" class="message assistant"><span class="message-avatar"><Icon name="sparkles" :size="18" /></span><div class="thinking"><i></i><i></i><i></i><span>正在查找与整理信息…</span></div></div>
      </div>
      <div class="composer-area"><div v-if="error" class="inline-error" role="alert">{{ error }}</div><form class="composer" @submit.prevent="send()"><textarea v-model="draft" rows="3" maxlength="5000" :disabled="sending" aria-label="输入你的问题" placeholder="输入你的问题，让知识开始流动…" @keydown="onKeydown"></textarea><div class="composer-toolbar"><span><Icon :name="mode === 'agent' ? 'sparkles' : 'book'" :size="15" />{{ mode === 'agent' ? '智能助手 · 支持多轮对话' : '知识库检索 · 单轮问答' }}</span><button class="icon-button primary" :disabled="!draft.trim() || sending" aria-label="发送问题"><Icon name="arrowUp" :size="19" /></button></div></form><p class="composer-note">Enter 发送 · Shift + Enter 换行 · 回答由 AI 生成，请结合原始资料核实</p></div>
    </section>
  </div>
</template>
