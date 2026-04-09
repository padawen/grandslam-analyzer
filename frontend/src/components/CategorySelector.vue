<template>
  <div class="flex flex-col items-center gap-2">
    <span class="section-label">Tournament Type</span>
    <div class="flex gap-2 flex-wrap justify-center">
      <button
        v-for="cat in categories"
        :key="cat.value"
        @click="emit('select-category', cat.value)"
        :class="['pill-btn', 'pill-btn--large', cat.value === 'grand_slam' ? 'pill-btn--amber' : 'pill-btn--indigo', currentCategory === cat.value ? 'active' : '']"
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
</style>
