<template>
  <div class="flex flex-col items-center gap-2">
    <span class="section-label">Tournament Type</span>
    <div class="cat-selector">
      <button
        v-for="cat in categories"
        :key="cat.value"
        @click="emit('select-category', cat.value)"
        :class="['cat-btn', currentCategory === cat.value ? `cat-btn--active cat-btn--active-${cat.value}` : '']"
      >
        {{ cat.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  availableCategories: { type: Array, default: () => ['grand_slam', 'masters'] },
  currentCategory: { type: String, required: true }
});
const emit = defineEmits(['select-category']);

const CATEGORY_META = {
  grand_slam: { label: 'Grand Slams', value: 'grand_slam' },
  masters: { label: 'Masters', value: 'masters' },
};

const categories = computed(() => {
  const order = ['grand_slam', 'masters'];
  return order
    .filter(v => props.availableCategories.includes(v))
    .map(v => CATEGORY_META[v]);
});
</script>

<style scoped>
.cat-selector {
  display: flex;
  gap: 6px;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  padding: 5px;
}

.cat-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 20px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  border: 1px solid transparent;
  background: transparent;
  transition: all 0.18s ease;
  white-space: nowrap;
}
.cat-btn:not(.cat-btn--active):hover {
  color: var(--text-secondary);
  background: rgba(255,255,255,0.04);
}
.cat-btn__icon { font-size: 15px; }

.cat-btn--active { cursor: default; }

.cat-btn--active-grand_slam,
.cat-btn--active-grand_slam:hover {
  background: rgba(245,158,11,0.12) !important;
  border-color: rgba(245,158,11,0.3) !important;
  color: var(--amber-light) !important;
  box-shadow: 0 0 16px rgba(245,158,11,0.1) !important;
}

.cat-btn--active-masters,
.cat-btn--active-masters:hover {
  background: rgba(16,185,129,0.12) !important;
  border-color: rgba(16,185,129,0.3) !important;
  color: var(--emerald-bright) !important;
  box-shadow: 0 0 16px rgba(16,185,129,0.1) !important;
}
</style>
