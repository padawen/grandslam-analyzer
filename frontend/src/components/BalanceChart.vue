<script setup>
import { ref, onMounted, watch } from 'vue';
import Chart from 'chart.js/auto';

const props = defineProps({
  matches: {
    type: Array,
    required: true
  },
  stake: {
    type: Number,
    default: 1000
  },
  roundOrder: {
    type: Array,
    required: true
  },
  isMobile: {
    type: Boolean,
    default: false
  }
});

const chartContainerRef = ref(null);
const chartInstance = ref(null);
const showRotationOverlay = ref(false);

onMounted(() => {
    renderMyChart();
    window.addEventListener('resize', checkOrientation);
    checkOrientation();
});

watch(() => [props.matches, props.stake], () => {
    renderMyChart();
}, { deep: true });

function formatNumber(num, decimals = 0) {
    if (typeof num !== 'number') return '0';
    return num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function checkOrientation() {
    if (chartContainerRef.value && chartContainerRef.value.classList.contains('chart-fullscreen')) {
        const isPortrait = window.matchMedia("(orientation: portrait)").matches;
        showRotationOverlay.value = isPortrait;
    } else {
        showRotationOverlay.value = false;
    }
}

function toggleChartFullscreen() {
    if (!chartContainerRef.value) return;
    const el = chartContainerRef.value;
    el.classList.toggle('chart-fullscreen');
    
    if (el.classList.contains('chart-fullscreen')) {
        document.body.style.overflow = 'hidden';
        checkOrientation();
    } else {
         document.body.style.overflow = '';
         showRotationOverlay.value = false;
    }
}

function renderMyChart() {
    const ctx = document.getElementById('balanceChart');
    if (!ctx) return;
    
    const matches = props.matches;
    const stakeAmt = props.stake;

    // Sort matches by match_time if available, otherwise by round and id
    const sortedMatches = [...matches].sort((a, b) => {
        // If both have match_time, sort by time
        if (a.match_time && b.match_time) {
            return new Date(a.match_time) - new Date(b.match_time);
        }
        // If only one has match_time, prioritize it
        if (a.match_time) return -1;
        if (b.match_time) return 1;
        
        // Fallback to round order
        const indexA = props.roundOrder.indexOf(a.round);
        const indexB = props.roundOrder.indexOf(b.round);
        if (indexA !== -1 && indexB !== -1) {
            if (indexA !== indexB) return indexA - indexB;
            return a.id - b.id;
        }
        if (indexA !== -1) return -1;
        if (indexB !== -1) return 1;
        return a.id - b.id;
    });

    const labels = ['Start'];
    const underdogData = [0];
    const favoriteData = [0];

    let uBal = 0;
    let fBal = 0;

    sortedMatches.forEach((match, index) => {
        if (!match.winner) return;

        // Underdog
        if (match.underdogWon) {
            uBal += (match.underdogOdds * stakeAmt) - stakeAmt;
        } else {
            uBal -= stakeAmt;
        }
        
        // Favorite
        const favOdds = Math.min(match.oddsA, match.oddsB);
        if (!match.underdogWon) {
            fBal += (favOdds * stakeAmt) - stakeAmt;
        } else {
            fBal -= stakeAmt;
        }

        labels.push(`${index + 1}.`);
        underdogData.push(uBal);
        favoriteData.push(fBal);
    });

    if (chartInstance.value) {
        chartInstance.value.destroy();
    }

    Chart.defaults.color = '#9ca3af';
    Chart.defaults.font.family = 'sans-serif';

    chartInstance.value = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Underdog Strategy',
                    data: underdogData,
                    borderColor: '#c084fc',
                    backgroundColor: 'rgba(192, 132, 252, 0.1)',
                    borderWidth: 3,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    tension: 0.1,
                    fill: true
                },
                {
                    label: 'Favorite Strategy',
                    data: favoriteData,
                    borderColor: '#60a5fa',
                    backgroundColor: 'rgba(96, 165, 250, 0.05)',
                    borderWidth: 3,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    tension: 0.1,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    onHover: (evt) => {
                        evt.native.target.style.cursor = 'pointer';
                    },
                    onLeave: (evt) => {
                        evt.native.target.style.cursor = 'default';
                    },
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: { size: 14, weight: 'bold' }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(20, 20, 20, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#e5e7eb',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                         title: function (context) {
                            const index = context[0].dataIndex;
                            if (index === 0) return 'Initial Balance';
                            const match = sortedMatches[index - 1];
                            return match ? `${match.underdog} vs ${match.favorite}` : '';
                        },
                        afterTitle: function (context) {
                             const index = context[0].dataIndex;
                            if (index === 0) return '';
                            const match = sortedMatches[index - 1];
                            if (!match) return '';
                            const winner = match.underdogWon ? match.underdog : match.favorite;
                            const odds = match.underdogWon ? match.underdogOdds : match.favoriteOdds;
                            const type = match.underdogWon ? "Underdog Win" : "Favorite Win";
                            
                            const lines = [
                                `${match.round}`,
                            ];
                            
                            // Add match time if available
                            if (match.match_time) {
                                const date = new Date(match.match_time);
                                const formatted = date.toLocaleString('en-US', {
                                    month: '2-digit',
                                    day: '2-digit',
                                    hour: '2-digit',
                                    minute: '2-digit',
                                    hour12: false
                                });
                                lines.push(formatted);
                            }
                            
                            lines.push(
                                `-------------------`,
                                `${type}`,
                                `Winner: ${winner}`,
                                `Odds: ${odds.toFixed(2)}`,
                                `-------------------`
                            );
                            
                            return lines;
                        },
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            if (context.parsed.y !== null) label += formatNumber(context.parsed.y, 0) + ' Units';
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)', borderColor: 'transparent' },
                    ticks: { maxTicksLimit: 20 }
                },
                y: {
                     grid: { color: 'rgba(255, 255, 255, 0.05)', borderColor: 'transparent' },
                     ticks: { callback: function (value) { return formatNumber(value, 0) + ' Units'; } }
                }
            }
        }
    });
}
</script>

<template>
    <div ref="chartContainerRef" class="bg-[#2a2a2a] border border-gray-700/50 rounded-2xl p-6 shadow-xl animate-fade-in mb-12 relative transition-all duration-300">
         <h3 class="text-2xl font-bold text-gray-200 mb-6 flex items-center justify-between gap-3">
            <div class="flex items-center gap-3">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
                Balance Trend
            </div>
            <button @click="toggleChartFullscreen" class="md:hidden text-gray-400 hover:text-white p-2 bg-black/20 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
            </button>
         </h3>

        <!-- Rotation Overlay -->
        <div v-if="showRotationOverlay" class="fixed inset-0 bg-[#1a1a1a] z-[100] flex flex-col items-center justify-center text-center p-8 landscape:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24 text-purple-500 mb-6 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            <h3 class="text-2xl font-bold text-white mb-2">Rotate your device!</h3>
            <p class="text-gray-400">Fullscreen mode is only available in landscape mode.</p>
            <button @click="toggleChartFullscreen" class="mt-8 px-6 py-2 border border-gray-600 rounded-lg text-gray-400 hover:text-white">Close</button>
        </div>
        
         <div class="bg-[#2a2a2a] border border-gray-700/50 rounded-lg py-2 px-4 text-sm text-gray-400 shadow-sm mb-4 inline-block">
            Tip: Click on the colored circles below to toggle strategies!
        </div>

        <div class="relative h-[400px] w-full">
            <canvas id="balanceChart"></canvas>
        </div>
    </div>
</template>

<style scoped>
.chart-fullscreen {
    position: fixed !important;
    top: 0;
    left: 0;
    width: 100vw !important;
    height: 100vh !important;
    z-index: 50;
    background-color: #1a1a1a;
    padding: 20px;
    border-radius: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
}
.chart-fullscreen canvas {
    height: 100% !important;
}
</style>
