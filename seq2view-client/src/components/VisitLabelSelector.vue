<template>
  <v-card tile>
  <v-container>
    <v-row><v-card-title>Selection {{ id }}</v-card-title></v-row>
    <v-row align="center">
      <v-col class="d-flex" v-if="labels.length > 0">
        <v-autocomplete
          v-model="selection.feature"
          :items="labels"
          item-text="name"
          label="Feature"
          return-object
        ></v-autocomplete>
      </v-col>
    </v-row>

    <v-row>
        <v-col>
          <v-slider
            label="Visit"
            v-model="selection.visit"
            class="align-center"
            :min="1"
            :max="shape.fields.visits"
          >
            <template v-slot:append>
              <v-text-field
                v-model="selection.visit"
                class="mt-0 pt-0"
                single-line
                type="number"
                style="width: 60px"
                :min="1"
                :max="shape.fields.visits"
              ></v-text-field>
            </template>
          </v-slider>
        </v-col>
      </v-row>

  </v-container>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'
import * as types from '../types'

const VisitLabelSelectorProps = Vue.extend({
  props: {
    id: String
  }
})

@Component
export default class VisitLabelSelector extends VisitLabelSelectorProps {
  data () {
    return {
      selection: {
        feature: {},
        visit: 1 // 1-based indexing instead of 0
      } as types.FeatureVisitSelection
    }
  }

  get shape (): types.Shape {
    return this.$store.state.shape
  }

  get labels (): types.Label[] {
    return this.$store.state.labels
  }

  @Watch('selection', { deep: true })
  setSelectedFeature () {
    const kwargs = {
      id: +this.id - 1,
      feature: this.$data.selection.feature,
      // Used 1-based indexing.
      visit: this.$data.selection.visit - 1
    }
    this.$store.commit('updateSelection', kwargs)
  }
}
</script>
