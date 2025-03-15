<script setup lang="ts">
  // import { ref, onMounted } from "vue";
  import Filter from "@/components/FilterView.vue";
  import Classify from "@/components/ClassifyView.vue";
  import {onMounted} from "vue";
  import SettingsView from "@/components/SettingsView.vue";
  import Samples from "@/components/Samples.vue";

  //
  // // API State
  // const filterData = ref<any>(null);
  // const classifyData = ref<any>(null);
  // const samples = ref<{ files: string }[]>([]);
  //
  // // Fetch data functions
  // const fetchFiles = async (type: "filter" | "classify" | "samples") => {
  //   try {
  //   const res = await fetch(`/api/next_${type}_file`);
  //   const data = await res;
  //   console.log(`Fetched ${type}:`, data);
  //
  //   if (type === "filter") filterData.value = data;
  //   else if (type === "classify") classifyData.value = data;
  //   else samples.value = data.files || [];
  // } catch (error) {
  //   console.error(`Error fetching ${type}:`, error);
  // }
  // };
  //
  // // Fetch on mount
  // onMounted(() => {
  //   fetchFiles("filter");
  //   fetchFiles("classify");
  //   fetchFiles("samples");
  //
  //   // Poll every 5 seconds
  //   setInterval(() => {
  //   fetchFiles("filter");
  //   fetchFiles("classify");
  //   fetchFiles("samples");
  // }, 5000);
  // });
</script>

<template>
  <header>
  </header>

  <main>
    <div class="container">
      <!-- name of each tab group should be unique -->
      <div class="tabs tabs-box">
        <input type="radio" name="my_tabs_6" class="tab" aria-label="Filter" checked="checked"  />
        <div class="tab-content bg-base-100 border-base-300 p-6">
          <Filter/>
        </div>

        <input type="radio" name="my_tabs_6" class="tab" aria-label="Classify" />
        <div class="tab-content bg-base-100 border-base-300 p-6">
          <Classify/>
        </div>

        <input type="radio" name="my_tabs_6" class="tab" aria-label="History" />
        <div class="tab-content bg-base-100 border-base-300 p-6">
          <Samples/>
        </div>

        <input type="radio" name="my_tabs_6" class="tab" aria-label="Settings" />
        <div class="tab-content bg-base-100 border-base-300 p-6">
          <SettingsView/>
        </div>
      </div>
    </div>

  </main>
</template>


