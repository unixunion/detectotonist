<script setup lang="ts">
  import Filter from "@/components/FilterView.vue";
  import Classify from "@/components/ClassifyView.vue";
  import SettingsView from "@/components/SettingsView.vue";
  import Samples from "@/components/Samples.vue";
  import SamplerToggle from "@/components/SamplerToggle.vue";
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

        <!-- Sampling Toggle Component (Right-Aligned) -->
<!--        <div class="tab-content bg-base-100 border-base-300 p-6">-->
          <SamplerToggle />
<!--        </div>-->

      </div>
    </div>

  </main>
</template>


