<template>
  <v-card tile>
  <v-container>
    <v-row><v-card-title>Dataset Selection</v-card-title></v-row>
    <v-row align="center">
      <v-col class="d-flex">
        <v-autocomplete
          :items="datasets"
          label="Dataset"
        ></v-autocomplete>
      </v-col>
    </v-row>

    <v-row>
        <v-col class="d-flex">
          <v-radio-group v-model="selections.collection" label="Collection" mandatory>
      <v-radio
        class="text-capitalize"
        v-for="collection in collections"
        :key="collection"
        :label="collection"
        :value="collection"
      ></v-radio>
    </v-radio-group>
        </v-col>
      </v-row>

      <v-row>
        <v-col class="d-flex">
          <v-radio-group v-model="selections.set" label="Set" mandatory>
      <v-radio
        class="text-capitalize"
        v-for="set in sets"
        :key="set"
        :label="set"
        :value="set"
      ></v-radio>
    </v-radio-group>
        </v-col>
      </v-row>

  </v-container>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class DatasetSubsetSelector extends Vue {
  data () {
    return {
      datasets: ['0001', '0002'],
      collections: ['processed', 'raw'],
      sets: ['train', 'test'],
      selections: {
        dataset: '',
        collection: '',
        set: ''
      }
    }
  }
}
</script>
