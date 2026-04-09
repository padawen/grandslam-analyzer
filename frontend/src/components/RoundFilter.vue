<script setup>
defineProps({
  availableRounds: { type: Array, required: true },
  selectedRounds: { type: Set, required: true },
  isSingleSelect: { type: Boolean, default: false }
});
const emit = defineEmits(['toggle-round', 'toggle-mode']);

function isActive(round, set) {
  return set.has(round);
}
</script>

<template>
  <div v-if="availableRounds.length > 0" class="flex flex-col items-center gap-2 w-full animate-slide-down">
    <div class="flex items-center gap-4">
      <span class="section-label">Filter by Round</span>
    </div>
    <div class="flex flex-wrap justify-center gap-2">
      <button
        @click="emit('toggle-round', 'all')"
        :class="['pill-btn', 'pill-btn--emerald', selectedRounds.size === 0 ? 'active' : '']"
      >
        All
      </button>
      <button
        v-for="round in availableRounds"
        :key="round"
        @click="emit('toggle-round', round)"
        :class="['pill-btn', 'pill-btn--emerald', isActive(round, selectedRounds) ? 'active' : '']"
      >
        {{ round }}
      </button>
    </div>

    <div class="mt-4">
       <button 
        @click="emit('toggle-mode', !isSingleSelect)" 
        :class="['mode-toggle', isSingleSelect ? 'mode-toggle--active' : '']"
      >
        <div class="mode-toggle__dot"></div>
        <span>Single Select Mode</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.mode-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-subtle);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  transition: all 0.2s;
  cursor: pointer;
}
.mode-toggle:hover {
  background: rgba(255,255,255,0.06);
  color: var(--text-secondary);
}
.mode-toggle--active {
  border-color: var(--emerald-light);
  color: var(--emerald-bright);
  background: var(--emerald-dim);
}
.mode-toggle__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  transition: all 0.2s;
}
.mode-toggle--active .mode-toggle__dot {
  background: var(--emerald-bright);
}
</style>
