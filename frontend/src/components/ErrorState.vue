<template>
    <div v-if="error" class="fixed inset-0 bg-black/90 flex items-center justify-center backdrop-blur-sm z-50">
        <div class="bg-red-900/20 border border-red-500/50 p-8 rounded-2xl max-w-md text-center">
            <div class="text-5xl mb-4">⚠️</div>
            <h3 class="text-xl font-bold text-red-400 mb-2">Error</h3>
            <p class="text-red-200">{{ error }}</p>
             <button @click="emit('retry')" class="mt-6 px-6 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg font-bold transition-colors">
                Retry
            </button>
        </div>
    </div>
</template>

<script setup>
defineProps({
  error: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['retry']);
</script>
