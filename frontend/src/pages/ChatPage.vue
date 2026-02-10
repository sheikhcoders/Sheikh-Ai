<template>
  <div class="chat-page">
    <Sidebar />
    <div class="main-content">
      <div class="messages-container">
        <ChatMessage v-for="msg in messages" :key="msg.id" :message="msg" />
      </div>
      <ChatInput @send="sendMessage" />
    </div>
    <ToolPanel />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import ChatMessage from '../components/ChatMessage.vue'
import ChatInput from '../components/ChatInput.vue'
import ToolPanel from '../components/ToolPanel.vue'

const messages = ref([
  { id: 1, role: 'assistant', content: 'Hello! How can I help you today?' }
])

const sendMessage = (content: string) => {
  messages.value.push({ id: Date.now(), role: 'user', content })
  // Logic to call backend API
}
</script>

<style scoped>
.chat-page {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}
.messages-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>
