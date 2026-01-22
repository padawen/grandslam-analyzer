<script setup>
defineProps({
  stats: {
    type: Object,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  colorClass: {
    type: String, // 'purple' or 'blue'
    default: 'purple'
  }
});

function formatNumber(num, decimals = 0) {
    if (typeof num !== 'number') return '0';
    return num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}
</script>

<template>
     <div :class="[
        'rounded-2xl bg-gradient-to-br border overflow-hidden shadow-2xl',
        colorClass === 'purple' ? 'from-purple-600/20 to-purple-800/20 border-purple-500/30' : 'from-blue-600/20 to-blue-800/20 border-blue-500/30'
     ]">
        <div class="p-8 space-y-8">
             <div class="flex items-center gap-4">
                <h2 class="text-3xl font-bold text-gray-100">{{ title }}</h2>
            </div>
            <div class="space-y-6">
                <div class="text-center p-6 bg-black/30 rounded-xl border border-white/5">
                    <p class="text-sm text-gray-400 mb-2 font-medium uppercase tracking-wide">Win Rate</p>
                    <p :class="['text-6xl font-black', colorClass === 'purple' ? 'text-purple-400' : 'text-blue-400']">
                        {{ formatNumber(stats.winRate, 1) }}%
                    </p>
                </div>
                 <div class="flex justify-between items-center p-5 bg-black/30 rounded-xl border border-white/5">
                    <div>
                        <p class="text-sm text-gray-400 mb-1">Wins</p>
                        <p class="text-3xl font-bold text-green-400">{{ stats.wins }}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-sm text-gray-400 mb-1">Losses</p>
                        <p class="text-3xl font-bold text-red-400">{{ stats.losses }}</p>
                    </div>
                </div>
                <div class="text-center p-5 bg-black/30 rounded-xl border border-white/5">
                     <p class="text-sm text-gray-400 mb-2 font-medium uppercase tracking-wide">Total Profit/Loss</p>
                     <p :class="['text-4xl font-bold', stats.totalProfit >= 0 ? 'text-green-400' : 'text-red-400']">
                        {{ stats.totalProfit >= 0 ? '+' : '' }} {{ formatNumber(stats.totalProfit, 0) }} Units
                     </p>
                </div>
                 <div :class="['text-center p-6 bg-black/30 rounded-xl border-2', colorClass === 'purple' ? 'border-purple-500/50' : 'border-blue-500/50']">
                    <p class="text-sm text-gray-400 mb-2 font-medium uppercase tracking-wide">ROI</p>
                    <p :class="['text-5xl font-black', stats.roi >= 0 ? 'text-green-400' : 'text-red-400']">
                        {{ stats.roi >= 0 ? '+' : '' }}{{ formatNumber(stats.roi, 1) }}%
                    </p>
                </div>
            </div>
        </div>
     </div>
</template>
