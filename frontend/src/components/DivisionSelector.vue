<template>
  <div class="flex flex-col items-center gap-2">
    <span class="section-label">Division</span>
    <div class="flex gap-2">
      <button
        v-for="div in availableDivisions"
        :key="div"
        @click="emit('select-division', div)"
        :class="['pill-btn', div === 'ATP' ? 'atp-btn' : 'wta-btn', currentDivision === div ? getDivisionActive(div) : '']"
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

function getDivisionActive(div) {
  return div === 'WTA' ? 'active-wta active-hover-none' : 'active-atp active-hover-none';
}
</script>

<style scoped>
.atp-btn:not(.active-hover-none):hover {
  border-color: rgba(56, 189, 248, 0.4) !important;
  background: rgba(56, 189, 248, 0.08) !important;
  color: #7dd3fc !important;
}
.wta-btn:not(.active-hover-none):hover {
  border-color: rgba(236, 72, 153, 0.4) !important;
  background: rgba(236, 72, 153, 0.08) !important;
  color: #f9a8d4 !important;
}
.active-hover-none { cursor: default !important; }

.active-wta {
  background: rgba(236, 72, 153, 0.18) !important;
  border-color: #f472b6 !important;
  color: #f9a8d4 !important;
  box-shadow: 0 0 16px rgba(236, 72, 153, 0.2) !important;
}
.active-atp {
  background: rgba(56, 189, 248, 0.18) !important;
  border-color: #38bdf8 !important;
  color: #7dd3fc !important;
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.2) !important;
}
</style>
