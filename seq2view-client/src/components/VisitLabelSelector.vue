<template>
  <v-card tile>
  <v-container>
    <v-row><v-card-title>{{ selection }}</v-card-title></v-row>
    <v-row align="center">
      <v-col class="d-flex">
        <v-autocomplete
          :items="featureLabels"
          label="Feature"
        ></v-autocomplete>
      </v-col>
    </v-row>

    <v-row>
        <v-col>
          <v-slider
            label="Visit"
            v-model="visit"
            class="align-center"
            :min="1"
            :max="nVisits"
          >
            <template v-slot:append>
              <v-text-field
                v-model="visit"
                class="mt-0 pt-0"
                single-line
                type="number"
                style="width: 60px"
                :min="1"
                :max="nVisits"
              ></v-text-field>
            </template>
          </v-slider>
        </v-col>
      </v-row>

  </v-container>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

const VisitLabelSelectorProps = Vue.extend({
  props: {
    selection: String
  }
})

@Component
export default class VisitLabelSelector extends VisitLabelSelectorProps {
  data () {
    return {
      featureLabels: ['Alkaline phosphatase', 'Na+'],
      nVisits: 100,
      visit: 1 // 1-based indexing instead of 0-based.
    }
  }
}
</script>
