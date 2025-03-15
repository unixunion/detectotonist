<script setup lang="ts">
import {onMounted, ref, nextTick} from "vue";

// Filter Data State
const filterData = ref<any>(null);
const samplingActive = ref<boolean>(false);
const audioPlayer = ref<HTMLAudioElement | null>(null);

// Fetch Filter Data
const fetchFilterData = async () => {
  try {
    const res = await fetch('/api/next_filter_file');
    filterData.value = await res.json();
    console.log("Fetched filter data:", filterData.value);

    // Wait for Vue to update the DOM, then reload audio
    // await nextTick();

    // Force audio to reload
    // if (audioPlayer.value) {
    //   audioPlayer.value.pause();
    //   audioPlayer.value.currentTime = 0;
    //   audioPlayer.value.load();  // Reload the audio file
    // }
  } catch (error) {
    console.error("Error fetching filter data:", error);
  }
};

// Handle Accept/Reject
const handleFilter = async (status: "accept" | "reject") => {
  if (!filterData.value) return;

  try {
    await fetch("/api/filter", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: filterData.value.filename,
        status,
      }),
    });

    // Fetch next file after action
    fetchFilterData();
  } catch (error) {
    console.error("Error filtering file:", error);
  }
};


// Fetch current sampler status
const fetchSamplerStatus = async () => {
  try {
    const res = await fetch("/api/sampler/status");
    const data = await res.json();
    samplingActive.value = data.sampling_active;
    console.log("Sampler Status:", data);
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
      console.log("Sampling toggled:", newState);
    } else {
      console.error("Failed to toggle sampling:", data.message);
    }
  } catch (error) {
    console.error("Error toggling sampling:", error);
  }
};

// Fetch filter files when component loads
onMounted(fetchFilterData);

onMounted(() => {
  fetchFilterData();
  fetchSamplerStatus();
  setInterval(() => {
    fetchFilterData();
    fetchSamplerStatus();
  }, 1000);
});

</script>

<template>
  <div class="card bg-base-100 shadow-md p-4">
    <!-- Show filtering UI only if both spectrogram and audio exist -->
    <div v-if="filterData?.spectrogram && filterData?.audio">
      <h2 class="text-lg font-bold">Data Capture</h2>
      <p class="text-sm text-gray-500">Click or say: Accept or Reject</p>

      <!-- Spectrogram Image -->
      <img
          :src="filterData.spectrogram"
          class="w-full rounded-md border shadow-lg my-4"
          alt="Spectrogram"
      />

      <!-- Audio Preview -->
      <audio :key="filterData.audio" ref="audioPlayer" controls class="w-full">
        <source :src="`${filterData.audio}?t=${Date.now()}`" type="audio/wav" />
        Your browser does not support the audio element.
      </audio>

      <!-- Accept / Reject Buttons -->
      <div class="flex justify-center gap-4 mt-4">
        <button class="btn btn-success" @click="handleFilter('accept')">Accept</button>
        <button class="btn btn-error" @click="handleFilter('reject')">Reject</button>
      </div>
    </div>

    <!-- If filterData is missing OR it doesn't contain spectrogram/audio -->
    <p v-else class="text-center text-gray-500">No samples to filter</p>

    <!-- Toggle Sampling Button -->
<!--    <div class="flex justify-center mt-4">-->
<!--      <button-->
<!--        :class="samplingActive ? 'btn btn-error' : 'btn btn-success'"-->
<!--        @click="toggleSampler"-->
<!--      >-->
<!--        {{ samplingActive ? "Stop Sampling" : "Start Sampling" }}-->
<!--      </button>-->
<!--    </div>-->

  </div>
</template>