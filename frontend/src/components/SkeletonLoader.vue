<script setup>
defineProps({
  type: {
    type: String,
    validator: (v) => ['stats', 'chart', 'list'].includes(v),
    default: 'list'
  },
  count: { type: Number, default: 1 }
});
</script>

<template>
  <div class="skeleton-container">
    <!-- Stats Skeleton -->
    <template v-if="type === 'stats'">
      <div v-for="i in 1" :key="i" class="skeleton-stats glass-card">
        <div class="skeleton-stats__header"></div>
        <div class="skeleton-stats__body">
          <div v-for="j in 4" :key="j" class="skeleton-row"></div>
        </div>
      </div>
    </template>

    <!-- Chart Skeleton -->
    <template v-else-if="type === 'chart'">
      <div class="skeleton-chart glass-card">
        <div class="skeleton-chart__title"></div>
        <div class="skeleton-chart__grid"></div>
      </div>
    </template>

    <!-- List Skeleton -->
    <template v-else>
      <div class="skeleton-list">
        <div v-for="i in count" :key="i" class="skeleton-item glass-card">
          <div class="skeleton-item__left">
            <div class="skeleton-circle"></div>
            <div class="skeleton-text-group">
              <div class="skeleton-text skeleton-text--title"></div>
              <div class="skeleton-text skeleton-text--subtitle"></div>
            </div>
          </div>
          <div class="skeleton-item__right"></div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.skeleton-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 0.3; }
  100% { opacity: 0.6; }
}

.skeleton-stats, .skeleton-chart, .skeleton-item, .skeleton-text, .skeleton-circle, .skeleton-row, .skeleton-chart__title, .skeleton-stats__header {
  animation: pulse 1.5s ease-in-out infinite;
  background: var(--bg-elevated);
}

.skeleton-stats { padding: 32px; min-height: 400px; }
.skeleton-stats__header { height: 24px; width: 200px; border-radius: 4px; margin-bottom: 24px; }
.skeleton-row { height: 60px; width: 100%; border-radius: var(--radius-md); margin-bottom: 1px; }

.skeleton-chart { padding: 32px; height: 340px; }
.skeleton-chart__title { height: 20px; width: 150px; border-radius: 4px; margin-bottom: 20px; }
.skeleton-chart__grid { height: 240px; width: 100%; border-radius: var(--radius-md); }

.skeleton-list { display: flex; flex-direction: column; gap: 12px; }
.skeleton-item { 
  display: flex; align-items: center; justify-content: space-between; 
  padding: 16px 20px; border-radius: var(--radius-md);
}
.skeleton-item__left { display: flex; align-items: center; gap: 16px; }
.skeleton-circle { width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0; }
.skeleton-text-group { display: flex; flex-direction: column; gap: 6px; }
.skeleton-text { border-radius: 4px; }
.skeleton-text--title { height: 14px; width: 180px; }
.skeleton-text--subtitle { height: 10px; width: 120px; }
.skeleton-item__right { height: 20px; width: 40px; border-radius: 4px; }
</style>
