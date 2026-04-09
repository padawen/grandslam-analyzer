<template>
  <div v-if="availableTournaments.length > 0" class="flex flex-col items-center gap-2 mt-4">
    <span class="section-label">Tournament</span>
    <div class="flex gap-2 flex-wrap justify-center">
      <button
        v-for="tournament in availableTournaments"
        :key="tournament.name"
        @click="emit('select-tournament', tournament.name)"
        :class="['pill-btn', currentTournamentName === tournament.name ? 'active' : '']"
        :title="tournament.surface"
      >
        {{ formatName(tournament.name) }} {{ tournament.year }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  availableTournaments: { type: Array, required: true },
  currentTournamentName: { type: String, default: "" }
});
const emit = defineEmits(['select-tournament']);

function formatName(name) {
  if (!name) return '';
  let clean = name.replace(/\b(wta|atp)\b/gi, '').replace(/\s{2,}/g, ' ').trim();
  clean = clean.replace(/Australian Open/gi, 'AO')
               .replace(/Roland Garros/gi, 'RG')
               .replace(/US Open/gi, 'USO')
               .replace(/Wimbledon/gi, 'WIMBLEDON');
  return clean.toUpperCase();
}
</script>

<style scoped>
</style>
