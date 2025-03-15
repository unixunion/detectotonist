<script setup lang="ts">
import {onMounted, ref} from "vue";
import {useTagsStore} from "@/stores/tags";


// TAG STORE
const tagsStore = useTagsStore();
onMounted(() => {
  tagsStore.fetchTags();
})


// Filter Data State
const classifyData = ref<any>(null);
const selectedTags = ref<any>([]);

// Fetch Filter Data
const fetchClassifyData = async () => {
  try {
    const res = await fetch('/api/next_classify_file');
    classifyData.value = await res.json();
    console.log("Fetched classify data:", classifyData.value);
  } catch (error) {
    console.error("Error fetching classify data:", error);
  }
};


// Handle setting a tag
const toggleTag = (tag: string) => {
  if (selectedTags.value.includes(tag)) {
    selectedTags.value = selectedTags.value.filter((t) => t !== tag);
  } else {
    selectedTags.value.push(tag);
  }
};


// Handle Accept/Reject
const handleClassify = async (status: "good" | "bad") => {
  if (!classifyData.value) {
    console.warn("No file to classify.");
    return;
  }

  try {
    const response = await fetch("/api/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: classifyData.value.filename,
        status,
        tags: selectedTags.value || []
      }),
    });

    const data = await response.json();
    if (data.status === "ok") {
      console.log("classification successful:", data.message);
      selectedTags.value = [];
      await fetchClassifyData();
    } else {
      console.error("classification failed:", data.message);
      selectedTags.value = [];
      await fetchClassifyData();
    }
    await fetchClassifyData();
  } catch (error) {
    console.error("Error classifying file:", error);
  }
};

// Fetch filter files when component loads
onMounted(fetchClassifyData);

onMounted(() => {
  fetchClassifyData();
  setInterval(() => {
    fetchClassifyData();
  }, 1000);
});

</script>

<template>
  <div class="card bg-base-100 shadow-md p-4">
    <div v-if="classifyData?.spectrogram && classifyData?.audio">
      <h2 class="text-lg font-bold">Classify</h2>
      <p class="text-sm text-gray-500">Click or say: Bad or Good</p>

      <!-- Spectrogram Image -->
      <img
          v-if="classifyData.spectrogram"
          :src="classifyData.spectrogram"
          class="w-full rounded-md border shadow-lg my-4"
          alt="Spectrogram"
      />

      <!-- Audio Preview -->
      <audio v-if="classifyData.audio" controls class="w-full">
        <source :src="classifyData.audio" type="audio/wav" />
        Your browser does not support the audio element.
      </audio>

      <!-- Tag Selection -->
      <div class="flex flex-wrap gap-2">
        <button
            v-for="tag in tagsStore.tags"
            :key="tag"
            @click="toggleTag(tag)"
            class="btn"
            :class="{
            'btn-outline': !selectedTags.includes(tag),
            'btn-primary': selectedTags.includes(tag),
          }"
        >
          {{ tag }}
        </button>
      </div>

      <!-- Accept / Reject Buttons -->
      <div class="flex justify-center gap-4 mt-4">
        <button class="btn btn-success" @click="handleClassify('good')">Good</button>
        <button class="btn btn-error" @click="handleClassify('bad')">Bad</button>
      </div>
    </div>

    <p v-else class="text-center text-gray-500">No samples to classify</p>
  </div>
</template>