<script setup lang="ts">
import { ref, onMounted } from "vue";

const samplingActive = ref(false);

// Fetch current sampler status
const fetchSamplerStatus = async () => {
  try {
    const res = await fetch("/api/sampler/status");
    const data = await res.json();
    samplingActive.value = data.sampling_active;
  } catch (error) {
    console.error("Error fetching sampler status:", error);
  }
};

// Toggle Sampling ON/OFF
const toggleSampler = async () => {
  try {
    const newState = !samplingActive.value;
    const res = await fetch("/api/sampler/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ active: newState }),
    });

    const data = await res.json();
    if (data.status === "ok") {
      samplingActive.value = newState; // Update state
    } else {
      console.error("Failed to toggle sampling:", data.message);
    }
  } catch (error) {
    console.error("Error toggling sampling:", error);
  }
};

// Fetch initial status on mount
onMounted(fetchSamplerStatus);
</script>

<template>
  <button
    :class="samplingActive ? 'btn btn-error' : 'btn btn-success'"
    @click="toggleSampler"
  >
    {{ samplingActive ? "Stop Sampling" : "Start Sampling" }}
  </button>
</template>