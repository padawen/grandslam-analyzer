<template>
    <div class="bg-[#2a2a2a] border border-gray-700/50 rounded-2xl p-4 md:p-6 shadow-xl">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
            <div class="flex flex-col md:flex-row md:items-center gap-3 md:gap-4">
                <h3 class="text-xl md:text-2xl font-bold text-gray-200 flex items-center gap-3">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 md:h-7 md:w-7 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    <span>All Matches <span class="text-gray-500 text-lg">({{ matches.length }})</span></span>
                </h3>
                <div v-if="isExpanded" class="bg-purple-600/20 border border-purple-500/30 rounded-lg px-3 py-1 text-xs text-purple-300 flex items-center gap-1 self-start md:self-auto">
                    <span class="text-purple-400 text-sm">★</span>
                    <span>= Underdog</span>
                </div>
            </div>
            <button @click="isExpanded = !isExpanded" class="w-full md:w-auto px-4 py-2 bg-[#3a3a3a] hover:bg-[#4a4a4a] rounded-lg text-gray-300 font-semibold transition-colors flex items-center justify-center gap-2">
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

            <div v-else>
                <!-- Desktop Table View -->
                <div class="hidden md:block overflow-x-auto">
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
                                        <span v-if="match.underdog === match.player_a && !isWalkover(match)" class="text-xs text-purple-400">★</span>
                                    </div>
                                </td>
                                <td class="text-center py-3 px-2 text-gray-600">-</td>
                                <td class="py-3 px-4">
                                    <div class="flex items-center gap-2">
                                        <span class="font-medium" :class="getPlayerColor(match, 'player_b')">
                                            {{ match.player_b }}
                                        </span>
                                        <span class="text-gray-400 font-mono text-xs">({{ match.oddsB?.toFixed(2) || '-' }})</span>
                                        <span v-if="match.underdog === match.player_b && !isWalkover(match)" class="text-xs text-purple-400">★</span>
                                    </div>
                                </td>
                                <td class="text-center py-3 px-3">
                                    <span v-if="isWalkover(match)" class="inline-block px-3 py-1 rounded-full text-xs font-bold bg-gray-600/20 text-gray-400 border border-gray-500/30">
                                        Walkover
                                    </span>
                                    <span v-else-if="match.underdogWon" class="inline-block px-3 py-1 rounded-full text-xs font-bold bg-purple-600/20 text-purple-400 border border-purple-500/30">
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

                <!-- Mobile Card View -->
                <div class="md:hidden space-y-4">
                    <div v-for="match in matches" :key="match.id" class="bg-[#333] rounded-xl p-4 border border-gray-700/50 shadow-sm relative overflow-hidden">
                        
                        <!-- Header with Round & Result Tag -->
                        <div class="flex justify-between items-start mb-3">
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-widest">{{ match.round }}</span>
                            <div>
                                 <span v-if="isWalkover(match)" class="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-600/20 text-gray-400 border border-gray-500/30 uppercase">
                                    Walkover
                                </span>
                                <span v-else-if="match.underdogWon" class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-600/20 text-purple-400 border border-purple-500/30 uppercase">
                                    Underdog Won
                                </span>
                                <span v-else-if="match.winner" class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-600/20 text-blue-400 border border-blue-500/30 uppercase">
                                    Favorite Won
                                </span>
                            </div>
                        </div>

                        <!-- Matchup -->
                        <div class="space-y-3">
                            <!-- Player A -->
                            <div class="flex justify-between items-center p-2 rounded-lg bg-black/20" :class="{'ring-1 ring-green-500/30 bg-green-900/10': getPlayerColor(match, 'player_a') === 'text-green-400'}">
                                <div class="flex items-center gap-2">
                                     <span class="font-bold" :class="getPlayerColor(match, 'player_a')">{{ match.player_a }}</span>
                                     <span v-if="match.underdog === match.player_a && !isWalkover(match)" class="text-xs text-purple-400">★</span>
                                </div>
                                <span class="font-mono text-sm text-gray-400 bg-black/40 px-2 py-1 rounded">{{ match.oddsA?.toFixed(2) || '-' }}</span>
                            </div>

                            <!-- VS divider -->
                            <!-- <div class="text-center text-xs text-gray-600 font-bold uppercase tracking-widest my-1">vs</div> -->

                             <!-- Player B -->
                            <div class="flex justify-between items-center p-2 rounded-lg bg-black/20" :class="{'ring-1 ring-green-500/30 bg-green-900/10': getPlayerColor(match, 'player_b') === 'text-green-400'}">
                                <div class="flex items-center gap-2">
                                     <span class="font-bold" :class="getPlayerColor(match, 'player_b')">{{ match.player_b }}</span>
                                     <span v-if="match.underdog === match.player_b && !isWalkover(match)" class="text-xs text-purple-400">★</span>
                                </div>
                                <span class="font-mono text-sm text-gray-400 bg-black/40 px-2 py-1 rounded">{{ match.oddsB?.toFixed(2) || '-' }}</span>
                            </div>
                        </div>

                    </div>
                </div>
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

function isWalkover(match) {
    return match.oddsA === 1.0 && match.oddsB === 1.0;
}

function getPlayerColor(match, player) {
    if (!match.winner) return 'text-gray-300';
    
    const winnerName = match.winner.trim();
    const playerName = player === 'player_a' ? match.player_a.trim() : match.player_b.trim();
    const isWinner = winnerName === playerName;
    
    return isWinner ? 'text-green-400' : 'text-red-400';
}
</script>
