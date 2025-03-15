<script setup lang="ts">
import {onMounted, ref} from "vue";

// Filter Data State
const filterData = ref<any>(null);

// Fetch Filter Data
const fetchFilterData = async () => {
  try {
    const res = await fetch('/api/next_filter_file');
    filterData.value = await res.json();
    console.log("Fetched filter data:", filterData.value);
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

// Fetch filter files when component loads
onMounted(fetchFilterData);

onMounted(() => {
  fetchFilterData();
  setInterval(() => {
    fetchFilterData();
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
      <audio controls class="w-full">
        <source :src="filterData.audio" type="audio/wav" />
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
  </div>
</template>