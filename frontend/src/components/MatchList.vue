<template>
    <div class="bg-[#2a2a2a] border border-gray-700/50 rounded-2xl p-6 shadow-xl">
        <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-4">
                <h3 class="text-2xl font-bold text-gray-200 flex items-center gap-3">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    All Matches ({{ matches.length }})
                </h3>
                <div v-if="isExpanded" class="bg-purple-600/20 border border-purple-500/30 rounded-lg px-3 py-1 text-xs text-purple-300 flex items-center gap-1">
                    <span class="text-purple-400 text-sm">★</span>
                    <span>= Underdog</span>
                </div>
            </div>
            <button @click="isExpanded = !isExpanded" class="px-4 py-2 bg-[#3a3a3a] hover:bg-[#4a4a4a] rounded-lg text-gray-300 font-semibold transition-colors flex items-center gap-2">
                <span>{{ isExpanded ? 'Hide' : 'Show' }}</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 transition-transform" :class="{ 'rotate-180': isExpanded }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
        </div>

        <div v-show="isExpanded">
            <div v-if="matches.length === 0" class="text-center py-12 text-gray-400">
                <p class="text-lg">No matches found for the selected filters</p>
            </div>

            <div v-else class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-gray-700">
                            <th class="text-left py-3 px-3 text-gray-400 font-semibold">Round</th>
                            <th class="text-left py-3 px-4 text-gray-400 font-semibold">Player A + Odds</th>
                            <th class="text-center py-3 px-2 text-gray-400 font-semibold">vs</th>
                            <th class="text-left py-3 px-4 text-gray-400 font-semibold">Player B + Odds</th>
                            <th class="text-center py-3 px-3 text-gray-400 font-semibold">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="match in matches" :key="match.id" class="border-b border-gray-800 hover:bg-[#333] transition-colors">
                            <td class="py-3 px-3 text-gray-300">{{ match.round }}</td>
                            <td class="py-3 px-4">
                                <div class="flex items-center gap-2">
                                    <span class="font-medium" :class="getPlayerColor(match, 'player_a')">
                                        {{ match.player_a }}
                                    </span>
                                    <span class="text-gray-400 font-mono text-xs">({{ match.oddsA?.toFixed(2) || '-' }})</span>
                                    <span v-if="match.underdog === match.player_a" class="text-xs text-purple-400">★</span>
                                </div>
                            </td>
                            <td class="text-center py-3 px-2 text-gray-600">-</td>
                            <td class="py-3 px-4">
                                <div class="flex items-center gap-2">
                                    <span class="font-medium" :class="getPlayerColor(match, 'player_b')">
                                        {{ match.player_b }}
                                    </span>
                                    <span class="text-gray-400 font-mono text-xs">({{ match.oddsB?.toFixed(2) || '-' }})</span>
                                    <span v-if="match.underdog === match.player_b" class="text-xs text-purple-400">★</span>
                                </div>
                            </td>
                            <td class="text-center py-3 px-3">
                                <span v-if="match.underdogWon" class="inline-block px-3 py-1 rounded-full text-xs font-bold bg-purple-600/20 text-purple-400 border border-purple-500/30">
                                    Underdog
                                </span>
                                <span v-else-if="match.winner" class="inline-block px-3 py-1 rounded-full text-xs font-bold bg-blue-600/20 text-blue-400 border border-blue-500/30">
                                    Favorite
                                </span>
                                <span v-else class="text-gray-600 text-xs">-</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  matches: {
    type: Array,
    required: true
  }
});

const isExpanded = ref(false);

function getPlayerColor(match, player) {
    if (!match.winner) return 'text-gray-300';
    
    const winnerName = match.winner.trim();
    const playerName = player === 'player_a' ? match.player_a.trim() : match.player_b.trim();
    const isWinner = winnerName === playerName;
    
    return isWinner ? 'text-green-400' : 'text-red-400';
}
</script>
