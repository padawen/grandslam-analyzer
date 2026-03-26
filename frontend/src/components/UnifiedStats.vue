<script setup>
const props = defineProps({
  underdog: { type: Object, required: true },
  favorite: { type: Object, required: true }
});

function formatNumber(num, decimals = 0) {
  if (typeof num !== 'number') return '0';
  return num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}
</script>

<template>
  <div class="unified-stats glass-card animate-fade-in">
    <!-- Header -->
    <div class="unified-stats__header">
      <div class="unified-stats__title-group">
        <h2 class="unified-stats__title">Performance Comparison</h2>
        <p class="unified-stats__subtitle">Underdog vs Favorite Strategy</p>
      </div>
      <div class="unified-stats__legend">
        <div class="legend-item"><span class="dot dot--underdog"></span> Underdog</div>
        <div class="legend-item"><span class="dot dot--favorite"></span> Favorite</div>
      </div>
    </div>

    <div class="metrics-list">
      <!-- 1. Win Rate -->
      <div class="metric-row">
        <div class="metric-row__label">Win Rate</div>
        <div class="metric-row__comparison">
          <div class="comp-val comp-val--underdog">
            <span class="text-emerald">{{ formatNumber(underdog.winRate, 1) }}%</span>
          </div>
          <div class="comp-bar-wrap">
            <div class="comp-bar comp-bar--underdog" :style="{ width: underdog.winRate + '%' }"></div>
            <div class="comp-bar comp-bar--favorite" :style="{ width: favorite.winRate + '%' }"></div>
          </div>
          <div class="comp-val comp-val--favorite">
            <span class="text-sky">{{ formatNumber(favorite.winRate, 1) }}%</span>
          </div>
        </div>
      </div>

      <!-- 2. Wins -->
      <div class="metric-row">
        <div class="metric-row__label">Match Results</div>
        <div class="metric-row__comparison">
          <div class="comp-val comp-val--underdog text-emerald-bright">
            {{ underdog.wins }} <span class="wins-label">WINS</span>
          </div>
          <div class="metric-row__spacer">/ {{ underdog.wins + underdog.losses }} matches total</div>
          <div class="comp-val comp-val--favorite text-sky">
            {{ favorite.wins }} <span class="wins-label">WINS</span>
          </div>
        </div>
      </div>

      <!-- 3. Profit / Loss -->
      <div class="metric-row">
        <div class="metric-row__label">Total Profit / Loss</div>
        <div class="metric-row__comparison">
          <div :class="['comp-pill', underdog.totalProfit >= 0 ? 'pill-emerald' : 'pill-red']">
            {{ underdog.totalProfit >= 0 ? '+' : '' }}{{ formatNumber(underdog.totalProfit) }}<u>u</u>
          </div>
          <div class="metric-row__spacer">Earnings</div>
          <div :class="['comp-pill', favorite.totalProfit >= 0 ? 'pill-emerald' : 'pill-red']">
            {{ favorite.totalProfit >= 0 ? '+' : '' }}{{ formatNumber(favorite.totalProfit) }}<u>u</u>
          </div>
        </div>
      </div>

      <!-- 4. ROI -->
      <div class="metric-row">
        <div class="metric-row__label">Return on Investment (ROI)</div>
        <div class="metric-row__comparison">
          <div :class="['comp-roi', underdog.roi >= 0 ? 'text-emerald' : 'text-red']">
             <div class="roi-label">UNDERDOG</div>
             <div class="roi-val">{{ underdog.roi >= 0 ? '+' : '' }}{{ formatNumber(underdog.roi, 1) }}%</div>
          </div>
          <div :class="['comp-roi', favorite.roi >= 0 ? 'text-sky' : 'text-red']">
             <div class="roi-label">FAVORITE</div>
             <div class="roi-val">{{ favorite.roi >= 0 ? '+' : '' }}{{ formatNumber(favorite.roi, 1) }}%</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.unified-stats {
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.unified-stats__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 24px;
}

.unified-stats__title { font-size: 20px; font-weight: 800; color: var(--text-primary); margin: 0; letter-spacing: -0.02em; }
.unified-stats__subtitle { font-size: 13px; color: var(--text-muted); margin: 4px 0 0; }

.unified-stats__legend { display: flex; gap: 48px; margin-top: 12px; }
.legend-item { 
  display: flex; 
  align-items: center; 
  gap: 16px; 
  font-size: 20px; 
  font-weight: 900; 
  text-transform: uppercase; 
  color: var(--text-primary); 
  letter-spacing: 0.1em; 
}
.dot { width: 18px; height: 18px; border-radius: 50%; }
.dot--underdog { background: var(--emerald-light); box-shadow: 0 0 20px var(--emerald-dim); }
.dot--favorite { background: var(--sky); box-shadow: 0 0 20px var(--sky-dim); }

.wins-label { font-size: 12px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.1em; margin-left: 4px; }

.metrics-list { display: flex; flex-direction: column; gap: 1px; background: var(--border-subtle); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); overflow: hidden; }

.metric-row { display: grid; grid-template-columns: 240px 1fr; align-items: center; background: var(--bg-card); padding: 24px 32px; }

.metric-row__label { font-size: 13px; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }

.metric-row__comparison { display: flex; align-items: center; justify-content: space-between; gap: 40px; }

.metric-row__spacer { font-size: 10px; font-weight: 800; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.1em; opacity: 0.5; }

.comp-val { min-width: 80px; font-size: 24px; font-weight: 900; letter-spacing: -0.02em; }
.comp-val--underdog { text-align: left; }
.comp-val--favorite { text-align: right; }

.comp-bar-wrap { flex: 1; height: 10px; background: rgba(255,255,255,0.05); border-radius: 10px; display: flex; gap: 4px; padding: 2px; }
.comp-bar { height: 100%; border-radius: 10px; transition: width 0.6s ease-out; }
.comp-bar--underdog { background: var(--emerald-light); box-shadow: 0 0 12px var(--emerald-dim); }
.comp-bar--favorite { background: var(--sky); box-shadow: 0 0 12px var(--sky-dim); }

.comp-details { display: flex; gap: 32px; }
.detail-item { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.detail-item span { font-size: 22px; font-weight: 800; }
.detail-item small { font-size: 9px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); }

.comp-pill { padding: 10px 24px; border-radius: 100px; font-size: 20px; font-weight: 800; border: 1px solid transparent; min-width: 140px; text-align: center; }
.comp-pill u { text-decoration: none; opacity: 0.6; font-size: 13px; margin-left: 2px; }
.pill-emerald { background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.2); color: #34d399; }
.pill-red { background: rgba(239, 68, 68, 0.08); border-color: rgba(239, 68, 68, 0.2); color: #f87171; }

.comp-roi { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 20px; border-radius: var(--radius-md); background: rgba(255,255,255,0.02); border: 1px solid var(--border-subtle); }
.roi-label { font-size: 9px; font-weight: 800; color: var(--text-muted); letter-spacing: 0.1em; }
.roi-val { font-size: 32px; font-weight: 900; }

.text-emerald-bright { color: var(--emerald-bright); }
.text-emerald { color: #34d399; }
.text-sky { color: var(--sky); }
.text-red { color: #f87171; }

@media (max-width: 900px) {
  .unified-stats { padding: 20px; gap: 24px; }
  .metric-row { grid-template-columns: 1fr; gap: 16px; padding: 20px; }
  .metric-row__comparison { gap: 12px; }
  .comp-val { font-size: 18px; min-width: 50px; }
  .comp-pill { font-size: 16px; padding: 8px 16px; min-width: 110px; }
  .roi-val { font-size: 24px; }
  .comp-bar-wrap { display: none; }
}

@media (max-width: 600px) {
  .unified-stats__header { flex-direction: column; gap: 16px; }
  .unified-stats__legend { gap: 24px; margin-top: 0; }
  .legend-item { font-size: 14px; gap: 8px; }
  .dot { width: 12px; height: 12px; }
  .unified-stats__subtitle { display: none; }
}
</style>
