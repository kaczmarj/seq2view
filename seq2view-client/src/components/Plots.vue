<template>
  <v-container>
    <h1 v-if="plotsAvailable">Plots</h1>
    <h1 v-else>Select options on the left side.</h1>

    <div v-if="featureVisitSelections[0].feature.name !== undefined">
      <v-row v-for="(selector, index) in featureVisitSelections" :key="index">
        <v-col>
          <LinePlot :id="index" />
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import LinePlot from "@/components/LinePlot.vue";
import * as types from "../types";

@Component({ components: { LinePlot } })
export default class Plots extends Vue {
  data() {
    return {};
  }

  get featureVisitSelections(): types.FeatureVisitSelection[] {
    return this.$store.state.selections;
  }

  get plotsAvailable() {
    return this.$store.state.selections[0].feature.name !== undefined;
  }
}
</script>
