<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import YearSelector from './components/YearSelector.vue';
import DivisionSelector from './components/DivisionSelector.vue';
import RoundFilter from './components/RoundFilter.vue';
import StatsCard from './components/StatsCard.vue';
import BiggestSurprise from './components/BiggestSurprise.vue';
import BalanceChart from './components/BalanceChart.vue';
import LoadingState from './components/LoadingState.vue';
import ErrorState from './components/ErrorState.vue';
import WelcomeModal from './components/WelcomeModal.vue';
import MatchList from './components/MatchList.vue';

// --- State ---
const matchesData = ref([]);
const allMatchesData = ref([]); 
const availableYears = ref([]);
const availableDivisions = ref([]);
const currentYear = ref(null);
const currentDivision = ref('ATP');
const selectedRounds = ref(new Set());
const stake = ref(1000);
const loading = ref(true);
const error = ref(null);
const tournamentName = ref('');
const showWelcomeModal = ref(true);

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || '';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'X-API-Key': API_KEY
  }
});

// --- Lifecycle ---

onMounted(async () => {
  await loadYears();
});

async function loadYears() {
    try {
        const response = await api.get(`/years`);
        availableYears.value = response.data;
        
        if (availableYears.value.length > 0) {
            const latest = availableYears.value[0];
            await loadDivisions(latest);
            loadYear(latest, currentDivision.value);
        } else {
            loadYear(2026, 'ATP');
        }
    } catch (err) {
        console.error("Failed to load years:", err);
        loadYear(2026, 'ATP');
    }
}

async function loadDivisions(year) {
    try {
        const response = await api.get(`/divisions?year=${year}`);
        availableDivisions.value = response.data;
        
        // Only set default if currentDivision is not available or not set
        if (availableDivisions.value.length > 0) {
            if (!currentDivision.value || !availableDivisions.value.includes(currentDivision.value)) {
                currentDivision.value = availableDivisions.value.includes('ATP') ? 'ATP' : availableDivisions.value[0];
            }
        }
    } catch (err) {
        console.error("Failed to load divisions:", err);
        availableDivisions.value = ['ATP'];
        currentDivision.value = 'ATP';
    }
}

async function loadYear(year, division) {
  currentYear.value = year;
  currentDivision.value = division;
  loading.value = true;
  error.value = null;
  selectedRounds.value.clear();

  // Load divisions for this year
  await loadDivisions(year);

  try {
    const response = await api.get(`/matches?year=${year}&division=${division}&limit=2000`);
    const rawMatches = response.data;
    
    allMatchesData.value = processMatches(rawMatches);
    // Sort by match_time if available
    allMatchesData.value.sort((a, b) => {
      if (a.match_time && b.match_time) {
        return new Date(a.match_time) - new Date(b.match_time);
      }
      return 0;
    });
    matchesData.value = allMatchesData.value;
    
    if (rawMatches.length > 0 && rawMatches[0].surface) {
       tournamentName.value = `Grand Slam ${year} (${rawMatches[0].surface}) - ${division}`;
    } else {
       tournamentName.value = `Grand Slam ${year} - ${division}`;
    }

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
    
    if (m.winner === 'player_a') {
        underdogWon = isPlayerAUnderdog; 
    } else if (m.winner === 'player_b') {
        underdogWon = !isPlayerAUnderdog; 
    }

    // Translate round names if needed, or keep as is if backend returns English
    // Currently backend returns Hungarian '1/64 döntő' etc. Map them?
    const roundMapping = {
        'Selejtező - 1. forduló': 'Q1',
        'Selejtező - 2. forduló': 'Q2',
        'Selejtező - 3. forduló': 'Q3',
        '1. forduló': 'R128',
        '2. forduló': 'R64',
        '3. forduló': 'R32',
        '4. forduló': 'R16',
        '1/64 döntő': 'R128', // Fallback/alias
        '1/32 döntő': 'R64',
        '1/16 döntő': 'R32',
        '1/8 döntő': 'R16',
        'Negyeddöntők': 'Quarterfinal',
        'Elődöntők': 'Semifinal',
        'Döntő': 'Final'
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

// --- Round Filter Logic ---
const roundOrder = [
    'Q1', 'Q2', 'Q3', 
    'R128', 'R64', 'R32', 'R16',
    'Quarterfinal', 'Semifinal', 'Final'
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
        selectedRounds.value.clear();
    } else {
        if (selectedRounds.value.has(round)) {
            selectedRounds.value.delete(round);
        } else {
            selectedRounds.value.add(round);
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

// --- Statistics Logic ---
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

// Watchers
watch(stake, () => {
   calculateAndDisplayStats();
});

</script>

<template>
  <div class="bg-[#1a1a1a] text-white min-h-screen p-4 md:p-8 font-sans">
    
    <div class="max-w-6xl mx-auto space-y-8 animate-fade-in">
        
        <header class="text-center space-y-3">
            <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                Grand Slam Analyzer
            </h1>
        </header>

         <!-- Controls -->
        <div class="flex flex-col items-center justify-center gap-6">

            <YearSelector 
                :availableYears="availableYears" 
                :currentYear="currentYear" 
                @select-year="(year) => loadYear(year, currentDivision)" 
            />

            <DivisionSelector 
                :availableDivisions="availableDivisions" 
                :currentDivision="currentDivision" 
                @select-division="(division) => loadYear(currentYear, division)" 
            />

            <div class="bg-[#2a2a2a] border border-gray-700/50 rounded-lg py-2 px-6 text-sm text-gray-300 shadow-sm -mt-2">
                Tip: You can select multiple rounds
            </div>

            <RoundFilter
                :availableRounds="availableRounds"
                :selectedRounds="selectedRounds"
                @toggle-round="toggleRound"
            />

             <!-- Stake Input -->
            <div class="max-w-md w-full mx-auto">
                <label for="stake" class="block text-sm font-medium text-gray-300 mb-2 text-center uppercase tracking-wider">
                    Stake Amount per Match (Units)
                </label>
                <input type="number" id="stake" v-model.number="stake" placeholder="Stake Amount"
                    class="w-full text-center text-3xl h-16 bg-[#2a2a2a] border border-gray-700 focus:border-purple-500 rounded-xl px-4 transition-colors focus:outline-none text-white shadow-md font-bold"
                    min="0">
            </div>

        </div>

        <BiggestSurprise :surprise="biggestSurprise" />

        <!-- Stats Comparison Cards -->
        <div class="grid md:grid-cols-2 gap-8">
            <StatsCard 
                title="Underdog Strategy" 
                :stats="underdogStats" 
                colorClass="purple" 
            />
            <StatsCard 
                title="Favorite Strategy" 
                :stats="favoriteStats" 
                colorClass="blue" 
            />
        </div>

        <BalanceChart 
            :matches="matchesData" 
            :stake="stake" 
            :roundOrder="roundOrder" 
            :isMobile="false" 
        />

        <MatchList :matches="matchesData" />

        <footer class="text-center text-sm text-gray-500 pt-12 pb-8">
            <p>{{ tournamentName || 'Loading data...' }}</p>
        </footer>

    </div>

    <LoadingState :isLoading="loading" />
    <ErrorState :error="error" @retry="loadYear(currentYear)" />
    <WelcomeModal :show="showWelcomeModal" @close="showWelcomeModal = false" />
    
  </div>
</template>

<style>
/* Global CSS Animations remain here as they are used across components */
@keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
}
.animate-fade-in {
    animation: fade-in 0.5s ease-out;
}

@keyframes slide-down {
     from { opacity: 0; transform: translateY(-10px); }
     to { opacity: 1; transform: translateY(0); }
}
.animate-slide-down {
     animation: slide-down 0.5s ease-out;
}

@keyframes slide-up {
     from { opacity: 0; transform: translateY(20px); }
     to { opacity: 1; transform: translateY(0); }
}
.animate-slide-up {
     animation: slide-up 0.5s ease-out;
}
</style>
