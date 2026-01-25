<template>
    <div v-if="show" class="fixed inset-0 bg-black/90 flex items-center justify-center z-[60]">
        <div class="bg-[#2a2a2a] border border-gray-700/50 p-6 md:p-8 rounded-2xl max-w-lg w-full mx-4 shadow-2xl relative">
            <button @click="emit('close')" class="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
            <h2 class="text-2xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                Welcome!
            </h2>
            <div class="space-y-4 text-gray-300 leading-relaxed">
                <p>This page analyzes which betting strategy would be more profitable in the long run for <strong>Grand Slam</strong> matches.</p>
                <div class="bg-black/30 p-4 rounded-xl border border-white/5 space-y-3">
                    <div class="flex items-start gap-3">
                        <div class="w-2 h-2 rounded-full bg-purple-400 mt-2 shrink-0"></div>
                        <div>
                             <strong class="text-purple-400">Underdog Strategy:</strong><br>
                             Always betting on the player with higher odds (less likely to win).
                        </div>
                    </div>
                    <div class="flex items-start gap-3">
                        <div class="w-2 h-2 rounded-full bg-blue-400 mt-2 shrink-0"></div>
                        <div>
                            <strong class="text-blue-400">Favorite Strategy:</strong><br>
                            Always betting on the player with lower odds (more likely to win).
                        </div>
                    </div>
                </div>
                <p class="text-sm text-gray-400 italic">The system calculates profit and ROI based on real historical odds.</p>
            </div>
             <button @click="emit('close')" class="mt-6 w-full py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-bold rounded-xl transition-all shadow-lg">
                Got it!
            </button>
        </div>
    </div>
</template>

<script setup>
defineProps({
  show: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['close']);
</script>
