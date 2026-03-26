<template>
  <div class="matchlist glass-card animate-fade-in">
    <!-- Header -->
    <div class="matchlist__header">
      <div class="matchlist__header-main">
        <div class="matchlist__title-row">
          <h3 class="matchlist__title">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Matches
          </h3>
          <span class="matchlist__count">{{ matches.length }}</span>
        </div>
        <button @click="isExpanded = !isExpanded" class="matchlist__toggle">
          {{ isExpanded ? 'Hide' : 'Show All' }}
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" :style="{transform: isExpanded ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s'}">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      <div v-if="isExpanded" class="matchlist__legend-wrap">
        <div class="matchlist__legend">
          <span style="color: #4ade80;">●</span> Winner
        </div>
        <div class="matchlist__legend">
          <span style="color: #f87171;">●</span> Loser
        </div>
        <div class="matchlist__legend">
          <span class="matchlist__legend-star">★</span> Underdog
        </div>
      </div>
    </div>

    <div v-show="isExpanded">
      <div class="matchlist__filters">
        <div class="matchlist__search-wrap">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="matchlist__search-icon"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input type="text" v-model="searchQuery" placeholder="Search by player name..." class="matchlist__search-input" />
        </div>
      </div>

      <div v-if="filteredMatches.length === 0" class="matchlist__empty">
        <p>Loading... or just reading slow serverless data?</p>
        <p style="font-size: 13px; margin-top: 8px; opacity: 0.7;">(Try a different name if the data doesn't appear!)</p>
      </div>

      <div v-else>
        <!-- Desktop Table -->
        <div class="matchlist__table-wrap matchlist--desktop">
          <table class="matchlist__table">
            <thead>
              <tr>
                <th>Round</th>
                <th>Player A</th>
                <th class="text-center">vs</th>
                <th>Player B</th>
                <th class="text-center">Result</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="match in filteredMatches" :key="match.id" class="matchlist__row">
                <td class="matchlist__round-cell">{{ match.round }}</td>
                <td>
                  <div class="matchlist__player">
                    <span :class="['matchlist__player-name', getPlayerColor(match, 'player_a')]">{{ match.player_a }}</span>
                    <span class="matchlist__odds">{{ match.oddsA?.toFixed(2) || '-' }}</span>
                    <span v-if="match.underdog === match.player_a && !isWalkover(match)" class="matchlist__underdog-star">★</span>
                  </div>
                </td>
                <td class="matchlist__vs">–</td>
                <td>
                  <div class="matchlist__player">
                    <span :class="['matchlist__player-name', getPlayerColor(match, 'player_b')]">{{ match.player_b }}</span>
                    <span class="matchlist__odds">{{ match.oddsB?.toFixed(2) || '-' }}</span>
                    <span v-if="match.underdog === match.player_b && !isWalkover(match)" class="matchlist__underdog-star">★</span>
                  </div>
                </td>
                <td class="text-center">
                  <span v-if="isWalkover(match)" class="matchlist__badge matchlist__badge--neutral">Walkover</span>
                  <span v-else-if="match.underdogWon" class="matchlist__badge matchlist__badge--underdog">Underdog</span>
                  <span v-else-if="match.winner" class="matchlist__badge matchlist__badge--favorite">Favorite</span>
                  <span v-else class="matchlist__badge matchlist__badge--pending">–</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="matchlist__cards matchlist--mobile">
          <div v-for="match in filteredMatches" :key="match.id" class="matchlist__card">
            <div class="matchlist__card-header">
              <span class="matchlist__card-round">{{ match.round }}</span>
              <span v-if="isWalkover(match)" class="matchlist__badge matchlist__badge--neutral">Walkover</span>
              <span v-else-if="match.underdogWon" class="matchlist__badge matchlist__badge--underdog">Underdog</span>
              <span v-else-if="match.winner" class="matchlist__badge matchlist__badge--favorite">Favorite</span>
            </div>
            <div class="matchlist__card-players">
              <div class="matchlist__card-player" :class="{'matchlist__card-player--winner': getPlayerColor(match, 'player_a') === 'win'}">
                <div class="matchlist__card-player-info">
                  <span class="matchlist__card-player-name" :class="getPlayerColor(match, 'player_a')">{{ match.player_a }}</span>
                  <span v-if="match.underdog === match.player_a && !isWalkover(match)" class="matchlist__underdog-star">★</span>
                </div>
                <span class="matchlist__card-odds">{{ match.oddsA?.toFixed(2) || '-' }}</span>
              </div>
              <div class="matchlist__card-player" :class="{'matchlist__card-player--winner': getPlayerColor(match, 'player_b') === 'win'}">
                <div class="matchlist__card-player-info">
                  <span class="matchlist__card-player-name" :class="getPlayerColor(match, 'player_b')">{{ match.player_b }}</span>
                  <span v-if="match.underdog === match.player_b && !isWalkover(match)" class="matchlist__underdog-star">★</span>
                </div>
                <span class="matchlist__card-odds">{{ match.oddsB?.toFixed(2) || '-' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({ matches: { type: Array, required: true } });
const isExpanded = ref(false);
const searchQuery = ref('');

const filteredMatches = computed(() => {
  if (!searchQuery.value) return props.matches;
  const q = searchQuery.value.toLowerCase();
  return props.matches.filter(m => 
    m.player_a.toLowerCase().includes(q) || 
    m.player_b.toLowerCase().includes(q)
  );
});

function isWalkover(match) {
  return match.oddsA === 1.0 && match.oddsB === 1.0;
}

function getPlayerColor(match, player) {
  if (!match.winner) return 'neutral';
  const winnerName = match.winner.trim();
  const playerName = player === 'player_a' ? match.player_a.trim() : match.player_b.trim();
  return winnerName === playerName ? 'win' : 'loss';
}
</script>

<style scoped>
.matchlist { padding: 24px; }

.matchlist__header { display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px; }
.matchlist__header-main { display: flex; justify-content: space-between; align-items: center; width: 100%; gap: 12px; }
.matchlist__title-row { display: flex; align-items: center; gap: 10px; }
.matchlist__title { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 700; color: var(--text-primary); margin: 0; }
.matchlist__title svg { width: 22px; height: 22px; color: var(--sky); flex-shrink: 0; }
.matchlist__count {
  background: rgba(255,255,255,0.06); border: 1px solid var(--border-subtle);
  border-radius: 100px; padding: 2px 10px;
  font-size: 12px; font-weight: 600; color: var(--text-muted);
}
.matchlist__legend-wrap { display: flex; gap: 8px; flex-wrap: wrap; }
.matchlist__legend {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 600; color: var(--text-muted);
  background: rgba(255,255,255,0.04); border: 1px solid var(--border-subtle);
  border-radius: 6px; padding: 4px 10px;
}
.matchlist__legend-star { color: var(--emerald-light); font-size: 14px; line-height: 1; }
.matchlist__toggle {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 16px; border-radius: 10px;
  background: rgba(255,255,255,0.05); border: 1px solid var(--border-default);
  color: var(--text-secondary); font-size: 13px; font-weight: 700;
  transition: all 0.2s; white-space: nowrap;
}
.matchlist__toggle:hover { background: rgba(255,255,255,0.1); color: var(--text-primary); }
.matchlist__toggle svg { width: 16px; height: 16px; }

@media (max-width: 600px) {
  .matchlist { padding: 16px; }
  .matchlist__legend { font-size: 11px; padding: 3px 8px; }
  .matchlist__toggle { padding: 6px 12px; font-size: 12px; }
}

.matchlist__empty { text-align: center; padding: 40px; color: var(--text-muted); font-size: 15px; }

.matchlist__table-wrap { overflow-x: auto; border-radius: 10px; border: 1px solid var(--border-subtle); }
.matchlist__table { width: 100%; border-collapse: collapse; font-size: 13px; }
.matchlist__table thead tr { background: rgba(255,255,255,0.025); }
.matchlist__table th { padding: 12px 14px; text-align: left; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted); border-bottom: 1px solid var(--border-subtle); }
.matchlist__row { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
.matchlist__row:hover { background: rgba(255,255,255,0.025); }
.matchlist__row td { padding: 10px 14px; }

.matchlist__round-cell { font-size: 12px; font-weight: 600; color: var(--text-muted); white-space: nowrap; }
.matchlist__vs { text-align: center; color: var(--text-muted); font-size: 12px; }
.matchlist__player { display: flex; align-items: center; gap: 6px; }
.matchlist__player-name { font-weight: 600; }
.matchlist__player-name.win { color: #4ade80; }
.matchlist__player-name.loss { color: #f87171; }
.matchlist__player-name.neutral { color: var(--text-secondary); }
.matchlist__odds { font-size: 11px; font-weight: 600; color: var(--text-muted); background: rgba(255,255,255,0.05); border-radius: 4px; padding: 2px 6px; font-variant-numeric: tabular-nums; }
.matchlist__underdog-star { font-size: 11px; color: var(--emerald-light); }

.matchlist__filters { margin-bottom: 20px; display: flex; justify-content: flex-start; }
.matchlist__search-wrap {
  position: relative; width: 100%; max-width: 320px;
  display: flex; align-items: center;
}
.matchlist__search-icon {
  position: absolute; left: 14px;
  color: var(--text-muted);
}
.matchlist__search-input {
  width: 100%; padding: 10px 14px 10px 40px;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px; outline: none;
  transition: all 0.2s;
}
.matchlist__search-input:focus {
  background: rgba(255,255,255,0.06);
  border-color: var(--sky);
}
.matchlist__search-input::placeholder { color: var(--text-muted); }

.matchlist__badge { display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: 0.04em; border-radius: 6px; padding: 3px 8px; }
.matchlist__badge--underdog { background: rgba(16,185,129,0.1); color: var(--emerald-light); border: 1px solid rgba(16,185,129,0.25); }
.matchlist__badge--favorite { background: rgba(56,189,248,0.1); color: var(--sky); border: 1px solid rgba(56,189,248,0.25); }
.matchlist__badge--neutral { background: rgba(255,255,255,0.05); color: var(--text-muted); border: 1px solid var(--border-subtle); }
.matchlist__badge--pending { color: var(--text-muted); }

.matchlist__cards { display: flex; flex-direction: column; gap: 10px; }
.matchlist__card {
  background: rgba(255,255,255,0.02); border: 1px solid var(--border-subtle);
  border-radius: 12px; padding: 14px; display: flex; flex-direction: column; gap: 12px;
}
.matchlist__card-header { display: flex; justify-content: space-between; align-items: center; }
.matchlist__card-round { font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted); }
.matchlist__card-players { display: flex; flex-direction: column; gap: 8px; }
.matchlist__card-player {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 12px; border-radius: 8px; background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.02); transition: all 0.15s;
}
.matchlist__card-player-info { display: flex; align-items: center; gap: 8px; }
.matchlist__card-player-name { font-size: 14px; font-weight: 600; }
.matchlist__card-player-name.win { color: #4ade80; }
.matchlist__card-player-name.loss { color: #f87171; }
.matchlist__card-player-name.neutral { color: var(--text-primary); }
.matchlist__card-odds {
  font-size: 12px; font-weight: 700; color: var(--text-muted);
  background: rgba(0,0,0,0.3); padding: 4px 8px; border-radius: 6px;
  font-variant-numeric: tabular-nums;
}

.matchlist--desktop { display: none; }
.matchlist--mobile { display: flex; }

@media (min-width: 768px) {
  .matchlist--desktop { display: block; }
  .matchlist--mobile { display: none !important; }
}

</style>
