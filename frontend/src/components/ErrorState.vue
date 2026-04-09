<template>
  <div v-if="error" class="error-overlay">
    <div class="error-box">
      <div class="error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
        </svg>
      </div>
      <h3 class="error-title">Something went wrong</h3>
      <p class="error-msg">{{ error }}</p>
      <button @click="emit('retry')" class="error-btn">
        Try Again
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({ error: { type: String, default: null } });
const emit = defineEmits(['retry']);
</script>

<style scoped>
.error-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.8);
  display: flex; align-items: center; justify-content: center;
  z-index: 50;
  backdrop-filter: blur(8px);
  padding: 16px;
}
.error-box {
  background: var(--bg-card);
  border: 1px solid rgba(244, 63, 94, 0.25);
  border-radius: var(--radius-xl);
  padding: 32px;
  max-width: 400px; width: 100%;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  text-align: center;
  box-shadow: 0 0 40px rgba(244, 63, 94, 0.1);
}
.error-icon {
  width: 52px; height: 52px;
  background: var(--rose-dim);
  border: 1px solid rgba(244,63,94,0.2);
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  color: var(--rose-light);
}
.error-icon svg { width: 26px; height: 26px; }
.error-title { font-size: 18px; font-weight: 700; color: var(--text-primary); margin: 0; }
.error-msg { font-size: 14px; color: var(--text-secondary); line-height: 1.5; margin: 0; }
.error-btn {
  margin-top: 8px;
  padding: 10px 28px;
  background: var(--rose);
  border-radius: var(--radius-md);
  color: #fff;
  font-size: 14px; font-weight: 700;
  border: none;
  transition: all 0.2s;
}
.error-btn:hover { background: var(--rose-light); transform: translateY(-1px); box-shadow: 0 6px 20px rgba(244,63,94,0.3); }
</style>
