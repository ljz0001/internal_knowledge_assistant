<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import Icon from './Icon.vue'
defineProps({ title: String, busy: Boolean })
const emit = defineEmits(['close'])
const dialog = ref(null)
let previousFocus
onMounted(() => { previousFocus = document.activeElement; dialog.value.showModal(); dialog.value.querySelector('input, textarea, select, button')?.focus() })
onUnmounted(() => previousFocus?.focus())
</script>
<template>
  <dialog ref="dialog" class="modal" aria-labelledby="modal-title" @cancel.prevent="!busy && emit('close')" @click="event => { if (event.target === dialog && !busy) emit('close') }">
    <header><h2 id="modal-title">{{ title }}</h2><button class="icon-button" :disabled="busy" aria-label="关闭对话框" @click="emit('close')"><Icon name="close" /></button></header>
    <slot />
  </dialog>
</template>
