<script setup lang="ts">
import {useTagsStore} from "@/stores/tags.ts";
import TagManager from "@/components/TagManager.vue";

const tagsStore = useTagsStore();
</script>

<template>
  <div class="card bg-base-100 shadow-md p-4">
    <div v-if="tagsStore.tags">
      <h2 class="text-lg font-bold">Settings</h2>
      <div class="flex justify-center">
        <TagManager/>
      </div>
    </div>

    <p v-else class="text-center text-gray-500">No samples to filter</p>
  </div>
</template>

<style scoped>

</style>