<script setup>
defineProps({ name: String, size: { type: [Number, String], default: 20 } })
const paths = {
  grid: 'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
  chat: 'M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8v.5z',
  book: 'M12 6C9 3 5 3 2 4v15c4-1 7-1 10 2 3-3 6-3 10-2V4c-3-1-7-1-10 2z M12 6v15',
  database: 'M21 5c0 2.2-4 4-9 4S3 7.2 3 5s4-4 9-4 9 1.8 9 4z M3 5v14c0 2.2 4 4 9 4s9-1.8 9-4V5 M3 12c0 2.2 4 4 9 4s9-1.8 9-4',
  settings: 'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z M9 3l-1 3-3 1-2 3 2 3v3l3 2 1 3h6l1-3 3-2v-3l2-3-2-3-3-1-1-3z',
  search: 'M21 21l-5-5 M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0z',
  arrow: 'M5 12h14 M13 6l6 6-6 6',
  arrowUp: 'M12 19V5 M5 12l7-7 7 7',
  plus: 'M12 5v14 M5 12h14',
  close: 'M6 6l12 12 M18 6 6 18',
  check: 'm5 12 4 4L19 6',
  chevron: 'm9 5 7 7-7 7',
  upload: 'M12 16V3 M7 8l5-5 5 5 M4 16v5h16v-5',
  file: 'M14 2H5v20h14V7z M14 2v5h5 M8 12h8 M8 16h6',
  clock: 'M12 7v5l3 2 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0z',
  refresh: 'M20 7A9 9 0 1 0 21 15 M20 2v6h-6',
  trash: 'M3 6h18 M9 6V3h6v3 M5 6l1 15h12l1-15 M10 10v7 M14 10v7',
  edit: 'm16 3 5 5-12 12-6 1 1-6z M13 6l5 5',
  sparkles: 'm12 2 3 7 7 3-7 3-3 7-3-7-7-3 7-3z',
  shield: 'M12 2 3 6v6c0 5 9 10 9 10s9-5 9-10V6z M8 12l3 3 5-6',
  users: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M9 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8z M17 4a4 4 0 0 1 0 7 M22 21v-2a4 4 0 0 0-3-4',
  copy: 'M9 9h12v12H9z M15 9V3H3v12h6',
  menu: 'M3 6h18 M3 12h18 M3 18h18',
  help: 'M9 9a3 3 0 1 1 5 2c-2 1-2 2-2 3 M12 17h.01 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0z',
  logout: 'M9 3H3v18h6 M9 12h12 M16 7l5 5-5 5',
}
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path :d="paths[name] || paths.file" /></svg>
</template>
