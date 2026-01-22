<template>
    <div v-if="availableDivisions.length > 0" class="bg-[#2a2a2a] p-2 rounded-xl border border-gray-700/50 flex gap-2 shadow-md">
        <button 
            v-for="div in availableDivisions" 
            :key="div" 
            @click="emit('select-division', div)" 
            class="px-6 py-2 rounded-lg font-bold text-sm transition-all"
            :style="getButtonStyle(div)">
            {{ div }}
        </button>
    </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  availableDivisions: {
    type: Array,
    required: true
  },
  currentDivision: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['select-division']);

const getButtonStyle = (div) => {
    if (props.currentDivision === div) {
        if (div === 'WTA') {
            return {
                background: 'linear-gradient(135deg, #ec4899 0%, #d946ef 100%)',
                color: 'white'
            };
        } else {
            return {
                background: '#2563eb',
                color: 'white'
            };
        }
    } else {
        return {
            background: '#3a3a3a',
            color: '#d1d5db'
        };
    }
};
</script>
