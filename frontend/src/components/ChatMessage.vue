<template>
  <div :class="['message', message.role]">
    <div class="content">{{ message.content }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  message: {
    id: number | string
    role: string
    content: string
  }
}>()
</script>

<style scoped>
.message {
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 8px;
}
.user {
  background: #e6f7ff;
  align-self: flex-end;
}
.assistant {
  background: #fff;
  align-self: flex-start;
}
</style>
