<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useTagsStore } from "@/stores/tags";

const tagsStore = useTagsStore();
const newTag = ref("");

// Fetch tags on mount
onMounted(() => {
  tagsStore.fetchTags();
});

const handleAddTag = async () => {
  await tagsStore.addTag(newTag.value);
  newTag.value = ""; // Clear input after adding
};

const handleDeleteTag = async (tag: string) => {
  await tagsStore.deleteTag(tag);
};
</script>

<template>
  <div>

    <div class="flex items-center gap-2 py-2">
      <input v-model="newTag" placeholder="New tag" class="input input-bordered flex-1" />
      <button @click="handleAddTag" class="btn btn-primary">Add Tag</button>
    </div>

    <div class="flex flex-wrap gap-2 mt-4 py-2">
      <div v-for="tag in tagsStore.tags" :key="tag" class="flex items-center gap-2 border rounded p-2">
        <span>{{ tag }}</span>
        <button @click="handleDeleteTag(tag)" class="btn btn-sm btn-error">✕</button>
      </div>
    </div>
  </div>
</template>