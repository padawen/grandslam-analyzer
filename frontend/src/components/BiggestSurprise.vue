<script setup>
defineProps({
  surprise: { type: Object, default: null }
});
</script>

<template>
  <div v-if="surprise" class="biggest-surprise animate-slide-down">
    <div class="biggest-surprise__badge">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
      </svg>
      Biggest Surprise
    </div>
    <div class="biggest-surprise__content">
      <span class="biggest-surprise__odds">{{ surprise.underdogOdds.toFixed(2) }}</span>
      <div class="biggest-surprise__match">
        <span class="biggest-surprise__winner">{{ surprise.underdog }}</span>
        <span class="biggest-surprise__vs">def.</span>
        <span class="biggest-surprise__loser">{{ surprise.favorite }}</span>
        <span class="biggest-surprise__round">{{ surprise.round }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.biggest-surprise {
  max-width: 640px;
  margin: 0 auto;
  background: rgba(245, 158, 11, 0.05);
  border: 1px solid rgba(245,158,11,0.25);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
  text-align: center;
}
.biggest-surprise__badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--amber);
}
.biggest-surprise__badge svg { width: 14px; height: 14px; }
.biggest-surprise__content {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}
.biggest-surprise__odds {
  font-size: 36px;
  font-weight: 900;
  color: var(--amber-light);
  letter-spacing: -0.03em;
  line-height: 1;
}
.biggest-surprise__match {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}
.biggest-surprise__winner { font-size: 16px; font-weight: 700; color: var(--text-primary); }
.biggest-surprise__vs { font-size: 12px; font-weight: 600; color: var(--text-muted); }
.biggest-surprise__loser { font-size: 14px; font-weight: 500; color: var(--text-secondary); }
.biggest-surprise__round {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  padding: 3px 8px;
}
</style>
