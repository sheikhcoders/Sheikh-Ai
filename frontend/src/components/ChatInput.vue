<template>
  <div class="chat-input">
    <a-input-search
      v-model:value="text"
      placeholder="Type a message..."
      enter-button="Send"
      size="large"
      @search="onSend"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const text = ref('')
const emit = defineEmits(['send'])

const onSend = () => {
  if (text.value.trim()) {
    emit('send', text.value)
    text.value = ''
  }
}
</script>

<style scoped>
.chat-input {
  padding: 20px;
  background: white;
  border-top: 1px solid #d9d9d9;
}
</style>
