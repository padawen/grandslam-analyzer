<script setup>
defineProps({
  availableYears: {
    type: Array,
    required: true
  },
  currentYear: {
    type: Number,
    required: true
  }
});

const emit = defineEmits(['select-year']);
</script>

<template>
    <!-- Year Selector -->
    <div v-if="availableYears.length > 0" class="bg-[#2a2a2a] p-3 rounded-2xl border border-gray-700/50 flex gap-3 shadow-lg flex-wrap justify-center">
        <button v-for="year in availableYears" :key="year" @click="emit('select-year', year)" 
            :class="['px-8 py-3 rounded-xl font-bold text-lg transition-all', currentYear === year ? 'bg-purple-600 text-white' : 'bg-[#3a3a3a] hover:bg-[#4a4a4a] text-gray-300']">
            AO {{ year }}
        </button>
    </div>
    <!-- Fallback if no years loaded yet (or empty) -->
    <div v-else class="bg-[#2a2a2a] p-3 rounded-2xl border border-gray-700/50 flex gap-3 shadow-lg">
        <button @click="emit('select-year', 2026)" class="px-8 py-3 rounded-xl font-bold text-lg bg-purple-600 text-white">
            AO 2026
        </button>
    </div>
</template>
