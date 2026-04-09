<script setup>
const props = defineProps({
  stats: { type: Object, required: true },
  title: { type: String, required: true },
  colorClass: { type: String, default: 'emerald' }
});

function formatNumber(num, decimals = 0) {
  if (typeof num !== 'number') return '0';
  return num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}
</script>

<template>
  <div :class="['stats-card', `stats-card--${colorClass}`]">
    <!-- Header -->
    <div class="stats-card__header">
      <div :class="['stats-card__icon', `stats-card__icon--${colorClass}`]">
        <svg v-if="colorClass === 'emerald'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      </div>
      <div>
        <p class="stats-card__label">Strategy</p>
        <h2 class="stats-card__title">{{ title }}</h2>
      </div>
    </div>

    <!-- Win Rate Big Number -->
    <div class="stats-card__win-rate">
      <span :class="['stats-card__win-rate-number', `stats-card__win-rate-number--${colorClass}`]">
        {{ formatNumber(stats.winRate, 1) }}<span class="stats-card__win-rate-pct">%</span>
      </span>
      <span class="stats-card__win-rate-label">Win Rate</span>
    </div>

    <!-- W/L Row -->
    <div class="stats-card__wl-row">
      <div class="stats-card__wl-item">
        <span class="stats-card__wl-count stats-card__wl-count--win">{{ stats.wins }}</span>
        <span class="stats-card__wl-label">Wins</span>
      </div>
      <div class="stats-card__divider"></div>
      <div class="stats-card__wl-item">
        <span class="stats-card__wl-count stats-card__wl-count--loss">{{ stats.losses }}</span>
        <span class="stats-card__wl-label">Losses</span>
      </div>
    </div>

    <!-- Profit -->
    <div class="stats-card__metric">
      <span class="stats-card__metric-label">Total Profit / Loss</span>
      <span :class="['stats-card__metric-value', stats.totalProfit >= 0 ? 'stats-card__metric-value--pos' : 'stats-card__metric-value--neg']">
        {{ stats.totalProfit >= 0 ? '+' : '' }}{{ formatNumber(stats.totalProfit, 0) }}
        <span class="stats-card__metric-unit">u</span>
      </span>
    </div>

    <!-- ROI -->
    <div :class="['stats-card__roi', `stats-card__roi--${colorClass}`]">
      <span class="stats-card__roi-label">ROI</span>
      <span :class="['stats-card__roi-value', stats.roi >= 0 ? 'stats-card__roi-value--pos' : 'stats-card__roi-value--neg']">
        {{ stats.roi >= 0 ? '+' : '' }}{{ formatNumber(stats.roi, 1) }}%
      </span>
    </div>
  </div>
</template>

<style scoped>
.stats-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 28px;
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  gap: 20px;
  transition: border-color 0.25s, box-shadow 0.25s;
}
.stats-card--emerald:hover { border-color: rgba(52,211,153,0.2); box-shadow: var(--shadow-card), 0 0 30px rgba(16,185,129,0.08); }
.stats-card--sky:hover { border-color: rgba(56,189,248,0.2); box-shadow: var(--shadow-card), 0 0 30px rgba(56,189,248,0.08); }

.stats-card__header { display: flex; align-items: center; gap: 14px; }
.stats-card__icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
}
.stats-card__icon--emerald { background: var(--emerald-dim); color: var(--emerald-light); }
.stats-card__icon--sky { background: var(--sky-dim); color: var(--sky); }
.stats-card__icon svg { width: 22px; height: 22px; }
.stats-card__label { font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); margin: 0 0 2px; }
.stats-card__title { font-size: 18px; font-weight: 700; color: var(--text-primary); margin: 0; }

.stats-card__win-rate {
  display: flex; flex-direction: column; align-items: center;
  background: rgba(255,255,255,0.025);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 20px;
  gap: 4px;
}
.stats-card__win-rate-number { font-size: 64px; font-weight: 900; line-height: 1; letter-spacing: -0.03em; }
.stats-card__win-rate-number--emerald { color: var(--emerald-light); }
.stats-card__win-rate-number--sky { color: var(--sky); }
.stats-card__win-rate-pct { font-size: 36px; }
.stats-card__win-rate-label { font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted); }

.stats-card__wl-row {
  display: flex; align-items: center; gap: 0;
  background: rgba(255,255,255,0.025);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  overflow: hidden;
}
.stats-card__wl-item { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 14px; gap: 4px; }
.stats-card__wl-count { font-size: 32px; font-weight: 800; line-height: 1; }
.stats-card__wl-count--win { color: #4ade80; }
.stats-card__wl-count--loss { color: #f87171; }
.stats-card__wl-label { font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted); }
.stats-card__divider { width: 1px; height: 48px; background: var(--border-subtle); }

.stats-card__metric {
  display: flex; justify-content: space-between; align-items: center;
  background: rgba(255,255,255,0.025);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 14px 18px;
}
.stats-card__metric-label { font-size: 12px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-muted); }
.stats-card__metric-value { font-size: 22px; font-weight: 800; }
.stats-card__metric-value--pos { color: #4ade80; }
.stats-card__metric-value--neg { color: #f87171; }
.stats-card__metric-unit { font-size: 14px; font-weight: 600; opacity: 0.7; margin-left: 2px; }

.stats-card__roi {
  display: flex; justify-content: space-between; align-items: center;
  border-radius: var(--radius-md);
  padding: 16px 18px;
}
.stats-card__roi--emerald { background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.2); }
.stats-card__roi--sky { background: rgba(56,189,248,0.06); border: 1px solid rgba(56,189,248,0.2); }
.stats-card__roi-label { font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); }
.stats-card__roi-value { font-size: 28px; font-weight: 900; letter-spacing: -0.02em; }
.stats-card__roi-value--pos { color: #4ade80; }
.stats-card__roi-value--neg { color: #f87171; }
</style>
