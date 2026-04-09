<template>
  <div class="flex flex-col items-center gap-2">
    <span class="section-label">Division</span>
    <div class="flex gap-2">
      <button
        v-for="div in availableDivisions"
        :key="div"
        @click="emit('select-division', div)"
        :class="['pill-btn', div === 'ATP' ? 'pill-btn--sky' : 'pill-btn--pink', currentDivision === div ? 'active' : '']"
      >
        {{ div }}
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  availableDivisions: { type: Array, required: true },
  currentDivision: { type: String, required: true }
});
const emit = defineEmits(['select-division']);

</script>

<style scoped>
.pill-btn.active { cursor: default; }
</style>
