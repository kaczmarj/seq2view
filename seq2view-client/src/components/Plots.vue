<template>
  <v-container>

    <h1>Plots</h1>

    <v-row
      v-for="(selector, index) in featureVisitSelections" :key="index">
      <v-col>
          <LinePlot :id="index" />
      </v-col>
    </v-row>

  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import LinePlot from '@/components/LinePlot.vue'
import * as types from '../types'

@Component({ components: { LinePlot } })
export default class Plots extends Vue {
  data () {
    return {
    }
  }

  get featureVisitSelections (): types.FeatureVisitSelection[] {
    return this.$store.state.selections
  }
}
</script>
