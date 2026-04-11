<template>
  <div v-if="isOpen" class="console-overlay">
    <div class="console-header">
      <span>🖥️ Console ({{ logs.length }})</span>
      <button @click="isOpen = false" class="close-btn">✕</button>
    </div>
    <div class="console-content">
      <div v-for="(log, i) in logs.slice(-50)" :key="i" :class="['log-line', log.type]">
        <span class="log-type">[{{ log.type.toUpperCase() }}]</span>
        <span class="log-time">{{ log.time }}</span>
        <span class="log-message">{{ log.message }}</span>
      </div>
    </div>
    <div class="console-footer">
      <button @click="logs = []" class="clear-btn">Clear</button>
      <button @click="toggleExpand" class="expand-btn">{{ isExpanded ? '↓' : '↑' }}</button>
    </div>
  </div>
  <button v-else @click="isOpen = true" class="console-toggle">📋</button>
</template>

<script setup>
import { reactive, ref } from 'vue'

const isOpen = ref(false)
const isExpanded = ref(true)
const logs = reactive([])

// Перехватываем console методы
const originalLog = console.log
const originalError = console.error
const originalWarn = console.warn

console.log = (...args) => {
  logs.push({
    type: 'log',
    message: args.map(arg => typeof arg === 'string' ? arg : JSON.stringify(arg)).join(' '),
    time: new Date().toLocaleTimeString(),
  })
  originalLog(...args)
}

console.error = (...args) => {
  logs.push({
    type: 'error',
    message: args.map(arg => typeof arg === 'string' ? arg : JSON.stringify(arg)).join(' '),
    time: new Date().toLocaleTimeString(),
  })
  originalError(...args)
}

console.warn = (...args) => {
  logs.push({
    type: 'warn',
    message: args.map(arg => typeof arg === 'string' ? arg : JSON.stringify(arg)).join(' '),
    time: new Date().toLocaleTimeString(),
  })
  originalWarn(...args)
}

// Перехватываем глобальные ошибки
window.addEventListener('error', (event) => {
  logs.push({
    type: 'error',
    message: `${event.message} at ${event.filename}:${event.lineno}`,
    time: new Date().toLocaleTimeString(),
  })
})

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}
</script>

<style scoped>
.console-overlay {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 300px;
  background: #222;
  color: #0f0;
  font-family: monospace;
  font-size: 12px;
  border-top: 2px solid #0f0;
  z-index: 9999;
  display: flex;
  flex-direction: column;
}

.console-toggle {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #333;
  color: #0f0;
  border: 2px solid #0f0;
  font-size: 24px;
  cursor: pointer;
  z-index: 9999;
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #111;
  border-bottom: 1px solid #0f0;
}

.close-btn {
  background: none;
  border: none;
  color: #0f0;
  cursor: pointer;
  font-size: 16px;
}

.console-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.log-line {
  padding: 4px 0;
  margin: 2px 0;
  border-left: 3px solid transparent;
}

.log-line.log {
  color: #0f0;
  border-left-color: #0f0;
}

.log-line.error {
  color: #f44;
  border-left-color: #f44;
}

.log-line.warn {
  color: #f90;
  border-left-color: #f90;
}

.log-type {
  font-weight: bold;
  margin-right: 5px;
}

.log-time {
  color: #888;
  margin-right: 5px;
}

.log-message {
  word-break: break-all;
}

.console-footer {
  display: flex;
  gap: 10px;
  padding: 10px;
  border-top: 1px solid #0f0;
}

.clear-btn,
.expand-btn {
  flex: 1;
  padding: 8px;
  background: #333;
  color: #0f0;
  border: 1px solid #0f0;
  cursor: pointer;
  font-family: monospace;
}
</style>
