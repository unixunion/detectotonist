<script setup lang="ts">
  import { ref } from "vue";
  import Filter from "@/components/FilterView.vue";
  import Classify from "@/components/ClassifyView.vue";
  import SettingsView from "@/components/SettingsView.vue";
  import Samples from "@/components/Samples.vue";
  import SamplerToggle from "@/components/SamplerToggle.vue";
  const activeTab = ref("filter");
</script>

<!--<template>-->
<!--  <header>-->
<!--  </header>-->

<!--  <main>-->
<!--  <div class="container">-->
<!--    &lt;!&ndash; Tab Navigation &ndash;&gt;-->
<!--    <div class="tabs flex border-b border-gray-400">-->
<!--      <button-->
<!--        @click="activeTab = 'filter'"-->
<!--        :class="activeTab === 'filter' ? 'bg-primary text-white' : 'text-gray-500'"-->
<!--        class="px-4 py-2 cursor-pointer"-->
<!--      >-->
<!--        Filter-->
<!--      </button>-->

<!--      <button-->
<!--        @click="activeTab = 'classify'"-->
<!--        :class="activeTab === 'classify' ? 'bg-primary text-white' : 'text-gray-500'"-->
<!--        class="px-4 py-2 cursor-pointer"-->
<!--      >-->
<!--        Classify-->
<!--      </button>-->

<!--      <button-->
<!--        @click="activeTab = 'history'"-->
<!--        :class="activeTab === 'history' ? 'bg-primary text-white' : 'text-gray-500'"-->
<!--        class="px-4 py-2 cursor-pointer"-->
<!--      >-->
<!--        History-->
<!--      </button>-->

<!--      <button-->
<!--        @click="activeTab = 'settings'"-->
<!--        :class="activeTab === 'settings' ? 'bg-primary text-white' : 'text-gray-500'"-->
<!--        class="px-4 py-2 cursor-pointer"-->
<!--      >-->
<!--        Settings-->
<!--      </button>-->

<!--      &lt;!&ndash; Sampling Toggle (Right-Aligned) &ndash;&gt;-->
<!--      <div class="ml-auto">-->
<!--        <SamplerToggle />-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; Tab Content &ndash;&gt;-->
<!--    <div class="p-4 bg-base-100 border border-gray-300 rounded-md">-->
<!--      <Filter v-if="activeTab === 'filter'" />-->
<!--      <Classify v-if="activeTab === 'classify'" />-->
<!--      <Samples v-if="activeTab === 'history'" />-->
<!--      <SettingsView v-if="activeTab === 'settings'" />-->
<!--    </div>-->
<!--  </div>-->
<!--</main>-->
<!--</template>-->


<template>
  <header></header>

  <main>
    <div class="container">
      <!-- Tab Navigation -->
      <div class="tabs flex items-center border-b border-gray-400">
        <div class="flex space-x-4">
          <button
            @click="activeTab = 'filter'"
            :class="activeTab === 'filter' ? 'bg-primary text-white' : 'text-gray-500'"
            class="px-4 py-2 cursor-pointer"
          >
            Filter
          </button>

          <button
            @click="activeTab = 'classify'"
            :class="activeTab === 'classify' ? 'bg-primary text-white' : 'text-gray-500'"
            class="px-4 py-2 cursor-pointer"
          >
            Classify
          </button>

          <button
            @click="activeTab = 'history'"
            :class="activeTab === 'history' ? 'bg-primary text-white' : 'text-gray-500'"
            class="px-4 py-2 cursor-pointer"
          >
            History
          </button>

          <button
            @click="activeTab = 'settings'"
            :class="activeTab === 'settings' ? 'bg-primary text-white' : 'text-gray-500'"
            class="px-4 py-2 cursor-pointer"
          >
            Settings
          </button>
        </div>

        <!-- Sampling Toggle (Right-Aligned) -->
        <div class="ml-auto">
          <SamplerToggle />
        </div>
      </div>

      <!-- Tab Content -->
      <div class="p-4 bg-base-100 border border-gray-300 rounded-md">
        <Filter v-if="activeTab === 'filter'" />
        <Classify v-if="activeTab === 'classify'" />
        <Samples v-if="activeTab === 'history'" />
        <SettingsView v-if="activeTab === 'settings'" />
      </div>
    </div>
  </main>

  <!-- Status Bar at the Bottom -->
  <footer class="fixed bottom-0 left-0 w-full bg-gray-800 text-white text-sm p-2 flex justify-between items-center">
    <span>Status: Connected</span>
    <span>Last Sample: {{ lastSampleTime }}</span>
  </footer>
</template>