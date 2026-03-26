<script setup>
defineProps({
  availableYears: { type: Array, required: true },
  currentYear: { type: Number, required: true }
});
const emit = defineEmits(['select-year']);
</script>

<template>
  <div class="flex flex-col items-center gap-2">
    <span class="section-label">Season</span>
    <div class="flex gap-2 flex-wrap justify-center">
      <button
        v-for="year in availableYears"
        :key="year"
        @click="emit('select-year', year)"
        :class="['pill-btn', currentYear === year ? 'active' : '']"
      >
        {{ year }}
      </button>
      <button
        v-if="!availableYears.length"
        @click="emit('select-year', 2026)"
        class="pill-btn active"
      >
        2026
      </button>
    </div>
  </div>
</template>
