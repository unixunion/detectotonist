<script setup lang="ts">
import {useTagsStore} from "@/stores/tags.ts";
import TagManager from "@/components/TagManager.vue";

const tagsStore = useTagsStore();

const handleShutdown = async () => {
  try {
    const res = await fetch(`/api/shutdown`, { method: "POST" });
    const data = await res.json();
    if (data.status === "ok") {
      console.log("Shutdown:");
    } else {
      console.error("Shutdown failed:", data.message);
    }
  } catch (error) {
    console.error("Error shutting down:", error);
  }
};


const handleRecalibrate = async () => {
  try {
    const res = await fetch(`/api/recalibrate`, { method: "POST" });
    const data = await res.json();
    if (data.status === "ok") {
      console.log("Recalibrate:");
    } else {
      console.error("Recalibrate failed:", data.message);
    }
  } catch (error) {
    console.error("Error recalibrating, ", error);
  }
};

</script>

<template>
  <div class="card bg-base-100 shadow-md p-4">
    <div v-if="tagsStore.tags">
      <h2 class="text-lg font-bold">Settings</h2>
      <div class="flex justify-center">
        <TagManager/>
      </div>
    </div>

    <div class="border-t border-gray-300 my-6 py-2">
      <p class="text-center text-gray-500 text-sm">System</p>
    </div>

    <div class="flex justify-center gap-4 mt-4">
      <button class="btn btn-success" @click="handleRecalibrate()">Recalibrate</button>
      <button class="btn btn-error" @click="handleShutdown()">Shutdown</button>
    </div>
  </div>
</template>

<style scoped>

</style>