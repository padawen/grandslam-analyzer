<script setup>
defineProps({
  availableRounds: {
    type: Array,
    required: true
  },
  selectedRounds: {
    type: Set,
    required: true
  }
});

const emit = defineEmits(['toggle-round']);

function isRoundSelected(round, selectedRoundsSet) {
    return selectedRoundsSet.has(round);
}
</script>

<template>
    <div v-if="availableRounds.length > 0" class="w-full max-w-5xl animate-slide-down">
        <div class="flex flex-wrap justify-center gap-3">
            <button @click="emit('toggle-round', 'all')"
                :class="['px-6 py-3 rounded-xl font-bold border-2 transition-all text-base', selectedRounds.size === 0 ? 'bg-[#2a2a2a] border-purple-500 text-purple-400' : 'bg-[#2a2a2a] border-gray-700 text-gray-300']">
                All
            </button>
            
            <button v-for="round in availableRounds" :key="round" @click="emit('toggle-round', round)"
                :class="['px-6 py-3 rounded-xl font-bold border-2 transition-all text-base', isRoundSelected(round, selectedRounds) ? 'bg-[#2a2a2a] border-purple-500 text-purple-400' : 'bg-[#2a2a2a] border-gray-700 text-gray-300']">
                {{ round }}
            </button>
        </div>
    </div>
</template>
