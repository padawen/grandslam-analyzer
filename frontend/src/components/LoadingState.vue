<template>
    <div v-if="isLoading" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
        <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-4 border-purple-500/30 border-t-purple-500 mx-auto mb-3"></div>
            <p class="text-purple-200 font-semibold">Analyzing data...</p>
        </div>
    </div>
</template>

<script setup>
defineProps({
  isLoading: {
    type: Boolean,
    required: true
  }
});
</script>
