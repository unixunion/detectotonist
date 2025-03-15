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
      console.error("Shutdown failed failed:", data.message);
    }
  } catch (error) {
    console.error("Error shutting down:", error);
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
    <div class="flex justify-center gap-4 mt-4">
        <button class="btn btn-success" @click="handleShutdown()">Shutdown</button>
    </div>
  </div>
</template>

<style scoped>

</style>