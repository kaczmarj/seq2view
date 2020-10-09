<template>
  <v-navigation-drawer
    app
    v-bind:value="showDrawer"
    clipped
    hide-overlay
    stateless
  >
    <v-container class="pa-0">
      <v-row>
        <v-col>
          <DatasetSubsetSelector />
        </v-col>
      </v-row>
      <v-container pa-0 v-if="showVisitLabelSelector">
        <v-row v-for="(selector, index) in featureVisitSelections" :key="index">
          <v-col>
            <VisitLabelSelector :id="index" />
          </v-col>
        </v-row>

        <v-row>
          <v-col align="center">
            <v-btn elevation="2" color="success" @click="addVisitLabelSelector"
              >Add</v-btn
            >
          </v-col>
          <v-col>
            <v-btn
              elevation="2"
              color="error"
              :disabled="featureVisitSelections.length < 2"
              @click="popVisitLabelSelector"
              >Remove</v-btn
            >
          </v-col>
        </v-row>
      </v-container>
    </v-container>
  </v-navigation-drawer>
</template>

<script lang="ts">
import DatasetSubsetSelector from "@/components/DatasetSubsetSelector.vue";
import VisitLabelSelector from "@/components/VisitLabelSelector.vue";
import { FeatureVisitSelection } from "../types";
import { Component, Vue } from "vue-property-decorator";

@Component({ components: { DatasetSubsetSelector, VisitLabelSelector } })
export default class Drawer extends Vue {
  get showDrawer(): boolean {
    return this.$store.state.showDrawer;
  }

  get featureVisitSelections(): FeatureVisitSelection[] {
    return this.$store.state.selections;
  }

  get showVisitLabelSelector() {
    return (
      this.$store.state.selectedDataset &&
      this.$store.state.selectedCollection &&
      this.$store.state.selectedSet
    );
  }

  addVisitLabelSelector() {
    this.$store.commit("addSelection");
  }

  popVisitLabelSelector() {
    this.$store.commit("popSelection");
  }
}
</script>
