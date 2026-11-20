<script setup>
import { ref } from 'vue'
import { api, getApiBase, validateApiBase } from '../api/client.js'
import { writeStorage } from '../utils/storage.js'
import Icon from '../components/Icon.vue'
const emit = defineEmits(['notify', 'reconnect'])
const base = ref(getApiBase())
const testing = ref(false)
const error = ref('')
const testResult = ref('')
async function test() {
  testing.value = true; error.value = ''; testResult.value = ''
  try { const value = validateApiBase(base.value); const result = await api.health(value); testResult.value = `连接成功 · API ${result.version || ''}` }
  catch (e) { error.value = e.message }
  finally { testing.value = false }
}
function save() {
  error.value = ''; testResult.value = ''
  try {
    const value = validateApiBase(base.value)
    if (!writeStorage('zhixu-api-base', value)) throw new Error('当前浏览器不允许保存设置，请检查存储权限')
    base.value = value; emit('notify', '接口地址已保存'); emit('reconnect')
  } catch (e) { error.value = e.message }
}
</script>
<template>
  <div class="page settings-page"><div class="page-heading"><div><div class="eyebrow">MAKE IT YOURS</div><h1>连接与设置</h1><p>连接企业服务，构建属于你的知识工作空间。</p></div></div><section class="panel settings-panel"><div class="section-heading"><div><h2>API 服务连接</h2><p>设置当前浏览器使用的后端接口地址。</p></div><span class="quick-icon purple"><Icon name="settings" /></span></div><form @submit.prevent="save"><label>接口基础地址<input v-model="base" required placeholder="/api" :disabled="testing" /></label><p class="field-help">本地开发推荐使用 /api。若填写完整后端地址，后端需允许该页面来源跨域访问。</p><div v-if="error" class="inline-error" role="alert">{{ error }}</div><div v-if="testResult" class="success-strip" role="status"><Icon name="check" :size="17" />{{ testResult }}</div><div class="inline settings-actions"><button type="button" class="button" :disabled="testing" @click="test"><Icon name="refresh" :size="17" :class="{ spinning: testing }" />{{ testing ? '测试中…' : '测试连接' }}</button><button class="button primary" :disabled="testing">保存设置</button></div></form></section><section class="panel settings-panel"><div class="section-heading"><div><h2>关于知序</h2><p>企业内部知识库与办公助手</p></div><span class="version-tag">v1.0.0</span></div><div class="about-grid"><div><Icon name="chat" /><strong>智能协作</strong><p>借助智能助手理解问题、查询知识与办公信息。</p></div><div><Icon name="book" /><strong>知识沉淀</strong><p>通过上传与审核流程，持续积累可靠的企业资料。</p></div></div><p class="muted small">服务连接测试检查 API 是否可达；模型、数据库与向量服务是否可用，以具体业务请求的结果为准。</p></section></div>
</template>
