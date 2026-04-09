<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import YearSelector from './components/YearSelector.vue';
import DivisionSelector from './components/DivisionSelector.vue';
import CategorySelector from './components/CategorySelector.vue';
import TournamentSelector from './components/TournamentSelector.vue';  
import RoundFilter from './components/RoundFilter.vue';
import UnifiedStats from './components/UnifiedStats.vue';
import BiggestSurprise from './components/BiggestSurprise.vue';
import BalanceChart from './components/BalanceChart.vue';
import SkeletonLoader from './components/SkeletonLoader.vue';
import ErrorState from './components/ErrorState.vue';
import WelcomeModal from './components/WelcomeModal.vue';
import MatchList from './components/MatchList.vue';

const allCategoryTournaments = ref([]);

const matchesData = ref([]);
const allMatchesData = ref([]); 
const availableYears = ref([]);
const availableDivisions = computed(() => {
    const tourneys = allCategoryTournaments.value || [];
    const divisions = [...new Set(tourneys.map(t => t.division))];
    return divisions.sort((a, b) => (a === 'ATP' ? -1 : 1));
});
const availableTournaments = computed(() => {
    const tourneys = allCategoryTournaments.value || [];
    const filtered = tourneys.filter(t => t.division === currentDivision.value);
    
    const unique = [];
    const seen = new Set();
    for (const t of filtered) {
        const clean = getCleanName(t.name);
        if (!seen.has(clean)) {
            seen.add(clean);
            unique.push({ ...t, name: clean });
        }
    }
    return unique;
});
const availableCategories = ref(['grand_slam']);
const currentYear = ref(null);
const currentDivision = ref('ATP');
const currentCategory = ref('grand_slam');
const currentTournamentId = ref(null);
const currentTournamentName = ref("");
const selectedRounds = ref(new Set());
const isSingleSelect = ref(false);
const stake = ref(1000);
const loading = ref(true);
const error = ref(null);
const tournamentName = ref('');
const showWelcomeModal = ref(!localStorage.getItem('welcomeClosed'));

function closeWelcomeModal() {
  showWelcomeModal.value = false;
  localStorage.setItem('welcomeClosed', 'true');
}

const lastUpdated = ref(null);
const matchesCache = new Map();

const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '/api' : 'http://localhost:8000');
const API_KEY = import.meta.env.VITE_API_KEY || '';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'X-API-Key': API_KEY
  }
});

function isWalkover(match) {
  return match.oddsA === 1.0 && match.oddsB === 1.0;
}


onMounted(async () => {
  await loadYears();
});

async function loadYears() {
    try {
        const response = await api.get(`/years`);
        availableYears.value = response.data;
        
        if (availableYears.value.length > 0) {
            const latest = availableYears.value[0];
            await loadCategories(latest);
            loadYear(latest, currentDivision.value, currentCategory.value);
        } else {
            loadYear(2026, 'ATP', 'grand_slam');
        }
    } catch (err) {
        console.error("Failed to load years:", err);
        loadYear(2026, 'ATP', 'grand_slam');
    }
}

async function loadCategories(year) {
    try {
        const response = await api.get(`/categories?year=${year}`);
        availableCategories.value = response.data;
        if (!availableCategories.value.includes(currentCategory.value)) {
            currentCategory.value = availableCategories.value[0] || 'grand_slam';
        }
    } catch (err) {
        console.error("Failed to load categories:", err);
        availableCategories.value = ['grand_slam'];
    }
}

function getCleanName(name) {
    if (!name) return '';
    let clean = name.replace(/\b(wta|atp)\b/gi, '').replace(/\s{2,}/g, ' ').trim();
    clean = clean.replace(/Australian Open/gi, 'AO')
                 .replace(/Roland Garros/gi, 'RG')
                 .replace(/US Open/gi, 'USO')
                 .replace(/Wimbledon/gi, 'WIMBLEDON');
    return clean.toUpperCase();
}

async function handleCategoryChange(category) {
    currentCategory.value = category;
    await loadTournaments(currentYear.value, category);
    
    // After loading tournaments for the new category, check divisions
    if (availableDivisions.value.length > 0) {
        if (!availableDivisions.value.includes(currentDivision.value)) {
            currentDivision.value = availableDivisions.value[0];
        }
    }
    
    // Auto-select first available tournament for the current division
    if (availableTournaments.value.length > 0) {
        const firstT = availableTournaments.value[0];
        await loadYear(currentYear.value, currentDivision.value, category, firstT.name, true);
    } else {
        await loadYear(currentYear.value, currentDivision.value, category, null, true);
    }
}

async function handleDivisionChange(division) {
    currentDivision.value = division;
    if (availableTournaments.value.length > 0) {
        const firstT = availableTournaments.value[0];
        await loadYear(currentYear.value, division, currentCategory.value, firstT.name, true);
    } else {
        await loadYear(currentYear.value, division, currentCategory.value, null, true);
    }
}

function toggleSingleSelect() {
    isSingleSelect.value = !isSingleSelect.value;
    selectedRounds.value = new Set();
    filterMatches();
}

async function loadTournaments(year, category) {
    try {
        const response = await api.get(`/tournaments_list?year=${year}&category=${category}`);
        allCategoryTournaments.value = response.data;

        if (availableTournaments.value.length > 0) {
            if (!currentTournamentName.value) {
                currentTournamentName.value = availableTournaments.value[0].name;
            } else {
                const stillExists = availableTournaments.value.some(t => t.name === currentTournamentName.value);
                if (!stillExists) {
                    currentTournamentName.value = availableTournaments.value[0].name;
                }
            }
        } else {
            currentTournamentName.value = "";
            currentTournamentId.value = null;
        }
    } catch (err) {
        console.error("Failed to load tournaments:", err);
        allCategoryTournaments.value = [];
        currentTournamentName.value = "";
        currentTournamentId.value = null;
    }
}

async function loadYear(year, division, category = currentCategory.value, tournamentNameAttr = null, forceResetRounds = false) {
  if (forceResetRounds) {
    selectedRounds.value = new Set();
  }

  const isSameTournament = !tournamentNameAttr || tournamentNameAttr === currentTournamentName.value;
  if (year === currentYear.value && division === currentDivision.value && category === currentCategory.value && isSameTournament && !forceResetRounds) {
    if (allMatchesData.value.length > 0) return;
  }

  currentYear.value = year;
  currentDivision.value = division;
  currentCategory.value = category;
  if (tournamentNameAttr) currentTournamentName.value = tournamentNameAttr;
  
  loading.value = true;
  error.value = null;
  
  // If we came from a high-level filter change OR it's a new tournament, reset rounds
  if (tournamentNameAttr !== currentTournamentName.value || forceResetRounds) {
    selectedRounds.value = new Set();
  }

  await loadTournaments(year, category);

  const matching = (allCategoryTournaments.value || []).find(t => 
    getCleanName(t.name) === currentTournamentName.value && t.division === currentDivision.value
  );
  if (matching) {
    currentTournamentId.value = matching.id;
  } else if (allCategoryTournaments.value?.length > 0) {
    const firstForName = allCategoryTournaments.value.find(t => getCleanName(t.name) === currentTournamentName.value);
    currentTournamentId.value = firstForName ? firstForName.id : allCategoryTournaments.value[0].id;
  }

  const cacheKey = `${year}-${currentDivision.value}-${category}-${currentTournamentId.value}`;
  if (matchesCache.has(cacheKey)) {
    const cached = matchesCache.get(cacheKey);
    allMatchesData.value = cached.matches;
    matchesData.value = cached.matches;
    lastUpdated.value = cached.lastUpdated;
    tournamentName.value = cached.tournamentName;
    console.log(`[Cache] Using cached data for ${cacheKey}`);
    
    loading.value = false;
    calculateAndDisplayStats();
    return;
  }
  try {
    let url = `/matches?limit=2000`;
    if (currentTournamentId.value) {
        url += `&tournament_id=${currentTournamentId.value}`;
    } else {
        url += `&year=${year}&division=${division}&category=${category}`;
    }
    
    const response = await api.get(url);
    const rawMatches = response.data;
    
    allMatchesData.value = processMatches(rawMatches);
    allMatchesData.value.sort((a, b) => {
      if (a.match_time && b.match_time) {
        return new Date(a.match_time) - new Date(b.match_time);
      }
      return 0;
    });
    matchesData.value = allMatchesData.value;

    const catLabel = category === 'masters' ? 'Masters / WTA 1000' : 'Grand Slam';
    const tourney = availableTournaments.value.find(t => t.id === currentTournamentId.value);
    
    let tName = tourney ? tourney.name : catLabel;
    if (tourney) {
      tName = tName.replace(/\b(wta|atp)\b/gi, '').replace(/\s{2,}/g, ' ').trim();
      tName = tName.replace(/Australian Open/gi, 'AO')
                   .replace(/Roland Garros/gi, 'RG')
                   .replace(/US Open/gi, 'USO');
    }
    
    const tSurface = tourney ? tourney.surface : (rawMatches.length > 0 && rawMatches[0].surface ? rawMatches[0].surface : '');

    if (tSurface) {
       tournamentName.value = `${tName} ${year} (${tSurface}) - ${division}`;
    } else {
       tournamentName.value = `${tName} ${year} - ${division}`;
    }

    if (category === 'masters') {
      tournamentName.value = tournamentName.value.toUpperCase();
    }

    if (rawMatches.length > 0) {
      const latestUpdate = rawMatches.reduce((latest, match) => {
        if (!match.updated_at) return latest;
        const matchTime = new Date(match.updated_at);
        return !latest || matchTime > latest ? matchTime : latest;
      }, null);
      lastUpdated.value = latestUpdate;
    }

    matchesCache.set(cacheKey, {
      matches: allMatchesData.value,
      lastUpdated: lastUpdated.value,
      tournamentName: tournamentName.value
    });
    
    loading.value = false;
    calculateAndDisplayStats();

  } catch (err) {
    console.error(err);
    error.value = `Failed to load ${year} data: ${err.message}`;
    loading.value = false;
  }
}

function processMatches(apiMatches) {
  return apiMatches.map(m => {
    const oddsA = m.odds_a || 0;
    const oddsB = m.odds_b || 0;
    let isPlayerAUnderdog = oddsA > oddsB;
    const underdogOdds = isPlayerAUnderdog ? oddsA : oddsB;
    const favoriteOdds = isPlayerAUnderdog ? oddsB : oddsA;
    let underdogWon = false;
    
    if (m.winner) {
        const winnerName = m.winner.trim();
        const playerAName = m.player_a.trim();
        const playerBName = m.player_b.trim();
        
        if (winnerName === playerAName) {
            underdogWon = isPlayerAUnderdog;
        } else if (winnerName === playerBName) {
            underdogWon = !isPlayerAUnderdog;
        }
    }

    const roundMapping = {
        'Selejtező - 1. forduló': 'Q1',
        'Selejtező - 2. forduló': 'Q2',
        'Selejtező - 3. forduló': 'Q3',
        '1. forduló': 'R128',
        '2. forduló': 'R64',
        '3. forduló': 'R32',
        '4. forduló': 'R16',
        '1/64 döntő': 'R128',
        '1/32 döntő': 'R64',
        '1/16 döntő': 'R32',
        '1/8 döntő': 'R16',
        'Negyeddöntők': 'QF',
        'Elődöntők': 'SF',
        'Döntő': 'F'
    };
    
    let roundEng = roundMapping[m.round_name] || m.round_name;

    return {
      ...m,
      round: roundEng, 
      underdog: isPlayerAUnderdog ? m.player_a : m.player_b,
      favorite: isPlayerAUnderdog ? m.player_b : m.player_a,
      underdogOdds,
      favoriteOdds, 
      underdogWon,
      oddsA,
      oddsB
    };
  });
}

const roundOrder = [
    'Q1', 'Q2', 'Q3', 
    'R128', 'R64', 'R32', 'R16',
    'QF', 'SF', 'F'
];

const availableRounds = computed(() => {
    const rounds = [...new Set(allMatchesData.value.map(m => m.round))]
        .filter(r => r)
        .sort((a, b) => {
            const indexA = roundOrder.indexOf(a);
            const indexB = roundOrder.indexOf(b);
            if (indexA !== -1 && indexB !== -1) return indexA - indexB;
            if (indexA !== -1) return -1;
            if (indexB !== -1) return 1;
            return a.localeCompare(b);
        });
    return rounds;
});

function toggleRound(round) {
    if (round === 'all') {
        selectedRounds.value = new Set();
    } else {
        if (isSingleSelect.value) {
            if (selectedRounds.value.has(round)) {
                selectedRounds.value.clear(); 
            } else {
                selectedRounds.value = new Set([round]);
            }
        } else {
            const next = new Set(selectedRounds.value);
            if (next.has(round)) {
                next.delete(round);
            } else {
                next.add(round);
            }
            selectedRounds.value = next;
        }
    }
    filterMatches();
}

function filterMatches() {
    if (selectedRounds.value.size === 0) {
        matchesData.value = allMatchesData.value;
    } else {
        matchesData.value = allMatchesData.value.filter(m => selectedRounds.value.has(m.round));
    }
    calculateAndDisplayStats();
}

const underdogStats = ref({ winRate: 0, wins: 0, losses: 0, totalProfit: 0, roi: 0 });
const favoriteStats = ref({ winRate: 0, wins: 0, losses: 0, totalProfit: 0, roi: 0 });
const biggestSurprise = ref(null);

function calculateAndDisplayStats() {
    const matches = matchesData.value;
    const currentStake = stake.value;

    underdogStats.value = calculateStrategy(matches, currentStake, 'underdog');
    favoriteStats.value = calculateStrategy(matches, currentStake, 'favorite');
    
    const wins = matches.filter(m => m.underdogWon);
    if (wins.length > 0) {
        biggestSurprise.value = wins.reduce((prev, curr) => (prev.underdogOdds > curr.underdogOdds) ? prev : curr);
    } else {
        biggestSurprise.value = null;
    }
}

function calculateStrategy(matches, stakeAmt, type) {
    if (!matches || matches.length === 0) return { winRate: 0, wins: 0, losses: 0, totalProfit: 0, roi: 0 };
    
    let wins = 0;
    let losses = 0;
    let totalProfit = 0;

    matches.forEach(match => {
        if (!match.winner) return;

        let betOdds, won;
        if (type === 'underdog') {
            betOdds = match.underdogOdds;
            won = match.underdogWon;
        } else {
            const favOdds = Math.min(match.oddsA, match.oddsB);
            betOdds = favOdds;
            won = !match.underdogWon;
        }
        
        if (isWalkover(match)) return;
        
        if (won) {
            wins++;
            totalProfit += (betOdds * stakeAmt) - stakeAmt;
        } else {
            losses++;
            totalProfit -= stakeAmt;
        }
    });

    const totalMatches = wins + losses; 
    const totalStaked = stakeAmt * totalMatches;
    const roi = totalStaked > 0 ? ((totalProfit / totalStaked) * 100) : 0;
    const winRate = totalMatches > 0 ? ((wins / totalMatches) * 100) : 0;

    return { winRate, wins, losses, totalProfit, roi };
}

watch(stake, () => {
   calculateAndDisplayStats();
});

</script>

<template>
  <div class="app-root">
    <div class="app-container animate-fade-in">

      <!-- Header -->
      <header class="app-header">
        <h1 class="app-header__title">Tennis Analyzer</h1>
        <p class="app-header__subtitle">Historical odds · Betting strategy simulator</p>
      </header>

      <!-- Controls -->
      <section class="controls-panel glass-card">
        <!-- 1. Season and Category (Tournament Type) -->
        <div class="controls-row">
          <YearSelector
            :availableYears="availableYears"
            :currentYear="currentYear"
            @select-year="(year) => loadYear(year, currentDivision, currentCategory)"
          />
        </div>

        <div class="controls-divider"></div>

        <div class="controls-row">
          <CategorySelector
            v-if="availableCategories.length > 1"
            :availableCategories="availableCategories"
            :currentCategory="currentCategory"
            @select-category="handleCategoryChange"
          />
        </div>

        <div class="controls-divider"></div>

        <div class="controls-row">
          <DivisionSelector
            v-if="availableDivisions.length > 0"
            :availableDivisions="availableDivisions"
            :currentDivision="currentDivision"
            @select-division="handleDivisionChange"
          />
        </div>

        <div class="controls-divider"></div>

        <TournamentSelector
          :availableTournaments="availableTournaments"
          :currentTournamentName="currentTournamentName"
          :currentDivision="currentDivision"
          @select-tournament="(tName) => loadYear(currentYear, currentDivision, currentCategory, tName)"
        />

        <div class="controls-divider"></div>

        <RoundFilter
          :availableRounds="availableRounds"
          :selectedRounds="selectedRounds"
          :isSingleSelect="isSingleSelect"
          @toggle-round="toggleRound"
          @toggle-mode="toggleSingleSelect"
        />

        <div class="controls-divider"></div>

        <!-- Stake Input -->
        <div class="stake-wrap">
          <label for="stake" class="section-label">Stake per Match</label>
          <div class="stake-input-row">
            <input
              type="number"
              id="stake"
              v-model.number="stake"
              min="0"
              class="stake-input"
              placeholder="1000"
            />
            <span class="stake-unit">units</span>
          </div>
        </div>
      </section>

      <!-- Content Area -->
      <div v-if="loading" class="skeletons-group">
        <SkeletonLoader type="stats" />
        <SkeletonLoader type="chart" />
        <SkeletonLoader type="list" :count="5" />
      </div>

      <template v-else>
        <BiggestSurprise :surprise="biggestSurprise" />
        
        <UnifiedStats
          :underdog="underdogStats"
          :favorite="favoriteStats"
        />

        <BalanceChart
          :matches="matchesData"
          :stake="stake"
          :roundOrder="roundOrder"
          :isMobile="false"
        />

        <MatchList :matches="matchesData" />
      </template>

      <!-- Footer -->
      <footer class="app-footer">
        <p>{{ tournamentName || 'Loading data...' }}</p>
        <p v-if="lastUpdated">Last updated: {{ lastUpdated.toLocaleString() }}</p>
      </footer>

    </div>

    <ErrorState :error="error" @retry="loadYear(currentYear)" />
    <WelcomeModal :show="showWelcomeModal" @close="closeWelcomeModal" />
  </div>
</template>

<style>
.app-root {
  min-height: 100vh;
  padding: 24px 16px 48px;
}

.app-container {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.skeletons-group {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.app-header {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px 0 8px;
}
.app-header__badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--emerald-light);
  background: var(--emerald-dim);
  border: 1px solid var(--border-accent);
  border-radius: 100px;
  padding: 5px 14px;
}
.app-header__badge svg { width: 13px; height: 13px; }
.app-header__title {
  font-size: clamp(32px, 6vw, 56px);
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1;
  color: var(--text-primary);
  margin: 0;
}
.app-header__subtitle {
  font-size: 14px;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: 0.03em;
  margin: 0;
}

.controls-panel {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
}
.controls-row {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
  justify-content: center;
  align-items: flex-end;
}
.controls-divider {
  width: 100%;
  height: 1px;
  background: var(--border-subtle);
}

.stake-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.stake-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.stake-input {
  width: 160px;
  text-align: center;
  font-size: 28px;
  font-weight: 800;
  height: 56px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  padding: 0 16px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: var(--font);
}
.stake-input:focus {
  border-color: var(--emerald-light);
  box-shadow: 0 0 0 3px rgba(52,211,153,0.12);
}
.stake-unit {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 640px) {
  .stats-grid { grid-template-columns: 1fr; }
  .controls-row { flex-direction: column; align-items: center; }
}

.app-footer {
  text-align: center;
  padding: 24px 0 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.app-footer p {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}
</style>
