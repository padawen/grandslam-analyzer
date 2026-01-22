<script setup>
defineProps({
  surprise: {
    type: Object, // allow null
    default: null
  }
});
</script>

<template>
    <div v-if="surprise" class="max-w-2xl mx-auto animate-slide-down">
        <div class="bg-gradient-to-r from-yellow-500/10 via-yellow-500/20 to-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 text-center">
            <div class="text-yellow-500 text-xs font-bold uppercase tracking-widest mb-1">Biggest Surprise</div>
            <div class="flex items-center justify-center gap-4 flex-wrap">
                <div class="text-3xl font-black text-white">{{ surprise.underdogOdds.toFixed(2) }}</div>
                <div class="text-lg font-bold text-yellow-400">{{ surprise.underdog }}</div>
                <div class="text-sm text-gray-400">vs {{ surprise.favorite }}</div>
                <div class="text-xs text-gray-500 bg-black/40 px-2 py-1 rounded ml-2">{{ surprise.round }}</div>
            </div>
        </div>
    </div>
</template>
