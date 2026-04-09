<template>
  <div v-if="show" class="modal-overlay" @click.self="emit('close')">
    <div class="modal" role="dialog" aria-modal="true">
      <button @click="emit('close')" class="modal__close" aria-label="Close">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div class="modal__icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2h-2" />
        </svg>
      </div>

      <h2 class="modal__title">Tennis Analyzer</h2>
      <p class="modal__subtitle">Betting strategy simulator using real historical odds</p>

      <div class="modal__strategies">
        <div class="modal__strategy modal__strategy--emerald">
          <div class="modal__strategy-dot modal__strategy-dot--emerald"></div>
          <div>
            <strong class="modal__strategy-title modal__strategy-title--emerald">Underdog Strategy</strong>
            <p class="modal__strategy-desc">Always betting on the player with higher odds (less likely to win).</p>
          </div>
        </div>
        <div class="modal__strategy modal__strategy--sky">
          <div class="modal__strategy-dot modal__strategy-dot--sky"></div>
          <div>
            <strong class="modal__strategy-title modal__strategy-title--sky">Favorite Strategy</strong>
            <p class="modal__strategy-desc">Always betting on the player with lower odds (more likely to win).</p>
          </div>
        </div>
      </div>

      <p class="modal__note">Profit & ROI calculated from real historical odds data.</p>

      <button @click="emit('close')" class="modal__cta">
        Let's Analyze
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { watch, onUnmounted } from 'vue';

const props = defineProps({
  show: { type: Boolean, required: true }
});
const emit = defineEmits(['close']);

watch(() => props.show, (val) => {
  document.body.style.overflow = val ? 'hidden' : '';
});
onUnmounted(() => { document.body.style.overflow = ''; });
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex; align-items: center; justify-content: center;
  z-index: 60;
  backdrop-filter: blur(8px);
  padding: 16px;
}

.modal {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: 32px;
  max-width: 440px;
  width: 100%;
  position: relative;
  box-shadow: 0 24px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.04);
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
  text-align: center;
}

.modal__close {
  position: absolute; top: 16px; right: 16px;
  background: rgba(255,255,255,0.06); border: 1px solid var(--border-subtle);
  border-radius: 8px; padding: 6px; line-height: 0;
  color: var(--text-muted); transition: all 0.15s;
}
.modal__close:hover { background: rgba(255,255,255,0.1); color: var(--text-primary); }
.modal__close svg { width: 16px; height: 16px; }

.modal__icon {
  width: 56px; height: 56px;
  background: var(--emerald-dim);
  border: 1px solid var(--border-accent);
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  color: var(--emerald-light);
}
.modal__icon svg { width: 28px; height: 28px; }

.modal__title {
  font-size: 22px; font-weight: 800;
  color: var(--text-primary); margin: 0;
}
.modal__subtitle {
  font-size: 14px; color: var(--text-secondary);
  margin: -8px 0 0; line-height: 1.5;
}

.modal__strategies {
  display: flex; flex-direction: column; gap: 10px;
  width: 100%;
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 14px;
}
.modal__strategy { display: flex; align-items: flex-start; gap: 12px; text-align: left; }
.modal__strategy-dot {
  width: 8px; height: 8px; border-radius: 50%;
  flex-shrink: 0; margin-top: 5px;
}
.modal__strategy-dot--emerald { background: var(--emerald-light); }
.modal__strategy-dot--sky { background: var(--sky); }
.modal__strategy-title { font-size: 13px; font-weight: 700; display: block; margin-bottom: 2px; }
.modal__strategy-title--emerald { color: var(--emerald-light); }
.modal__strategy-title--sky { color: var(--sky); }
.modal__strategy-desc { font-size: 12px; color: var(--text-secondary); line-height: 1.5; }

.modal__note {
  font-size: 12px; color: var(--text-muted);
  font-style: italic; margin: 0;
}

.modal__cta {
  width: 100%;
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 14px 24px;
  background: var(--emerald);
  border-radius: var(--radius-md);
  color: #000;
  font-size: 14px; font-weight: 700; letter-spacing: 0.02em;
  transition: all 0.2s;
  border: none;
}
.modal__cta:hover {
  background: var(--emerald-light);
  transform: translateY(-1px);
}
.modal__cta svg { width: 16px; height: 16px; }
</style>
