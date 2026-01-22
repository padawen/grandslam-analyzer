<template>
    <div v-if="isLoading" class="fixed inset-0 bg-black/80 flex items-center justify-center backdrop-blur-sm z-50">
        <div class="text-center">
            <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-500 mb-4 mx-auto"></div>
            <p class="text-purple-200 font-bold animate-pulse">Analyzing data...</p>
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
