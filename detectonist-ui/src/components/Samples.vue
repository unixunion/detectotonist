<script setup lang="ts">
import {ref, onMounted} from "vue";

const samples = ref<string[]>([]);

const fetchSamples  = async () => {
  try {
    const res = await fetch("/api/samples");
    const data = await res.json();
    if (data.status === "ok") {
      samples.value = data.files;
      console.log("got samples", samples.value);
    } else {
      console.log("Error fetching samples...");
      samples.value = [];
    }
  } catch (error) {
    console.log("Error fetching samples...", error);
  }
};

// Handle delete sample
const deleteSample = async (filename: string) => {
  try {
    const res = await fetch(`/api/samples/delete/${filename}`, { method: "POST" });
    const data = await res.json();

    if (data.status === "ok") {
      console.log("Deleted:", filename);
      fetchSamples(); // Refresh list
    } else {
      console.error("Delete failed:", data.message);
    }
  } catch (error) {
    console.error("Error deleting sample:", error);
  }
};

// Handle reclassify sample
const reclassifySample = async (filename: string) => {
  try {
    const res = await fetch(`/api/samples/reclassify/${filename}`, { method: "POST" });
    const data = await res.json();

    if (data.status === "ok") {
      console.log("Reclassified:", filename);
      fetchSamples(); // Refresh list
    } else {
      console.error("Reclassify failed:", data.message);
    }
  } catch (error) {
    console.error("Error reclassifying sample:", error);
  }
};

// Fetch samples on component mount
onMounted(() => {
  fetchSamples()
  setInterval(() => {
    fetchSamples();
  }, 1000);
})

</script>

<template>
  <div class="card bg-base-100 shadow-md p-4">
    <h2 class="text-lg font-bold">Samples</h2>
    <p class="text-sm text-gray-500">Manage previously classified files</p>

    <div v-if="samples.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mt-4">
      <div v-for="filename in samples" :key="filename" class="border rounded-lg p-2 shadow-lg">
        <img
            :src="`/api/files/samples/${filename}`"
            class="w-full rounded-md border"
            alt="Sample"
        />
        <p class="truncate text-center mt-2">{{ filename }}</p>

        <div class="flex justify-center gap-2 mt-3">
          <button class="btn btn-warning btn-sm" @click="reclassifySample(filename)">Reclassify</button>
          <button class="btn btn-error btn-sm" @click="deleteSample(filename)">Delete</button>
        </div>
      </div>
    </div>

    <p v-else class="text-center text-gray-500 mt-4">No samples available</p>
  </div>
</template>

<style scoped>

</style>