<template>
  <v-card tile>
    <v-container>
      <v-row><v-card-title>Dataset Selection</v-card-title></v-row>
      <v-row align="center">
        <v-col class="d-flex">
          <v-autocomplete
            :items="this.$store.state.datasets"
            v-model="selections.dataset"
            label="Dataset"
            @input="getCollections"
          ></v-autocomplete>
        </v-col>
      </v-row>

      <v-row v-if="this.$store.state.collections.length > 0">
        <v-col class="d-flex">
          <v-radio-group
            v-model="selections.collection"
            label="Collection"
            mandatory
          >
            <v-radio
              class="text-capitalize"
              v-for="collection in this.$store.state.collections"
              :key="collection"
              :label="collection"
              :value="collection"
            ></v-radio>
          </v-radio-group>
        </v-col>
      </v-row>

      <v-row v-if="this.$store.state.sets.length > 0">
        <v-col class="d-flex">
          <v-radio-group v-model="selections.set" label="Set" mandatory>
            <v-radio
              class="text-capitalize"
              v-for="set in this.$store.state.sets"
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
import { Component, Vue, Watch } from 'vue-property-decorator'
import axios from 'axios'
import * as types from '../types'

@Component
export default class DatasetSubsetSelector extends Vue {
  data () {
    return {
      selections: {
        dataset: '',
        collection: '',
        set: ''
      }
    }
  }

  async mounted () {
    try {
      const response = await axios.get<types.DatasetsResponse>(
        'http://127.0.0.1:5000/api/datasets'
      )
      this.$store.commit('setDatasets', response.data)
    } catch (error) {
      console.log(error)
    }
  }

  @Watch('selection.dataset')
  setDataset () {
    console.log(`DATASET: ${this.$data.selections.dataset}`)
    this.$store.commit('setSelectedDataset', this.$data.selections.dataset)
  }

  async getCollections () {
    this.setDataset() // This is necessary the first time if only one dataset exists.
    try {
      const response = await axios.get<types.DatasetInfoResponse>(
        `http://127.0.0.1:5000/api/datasets/${this.$data.selections.dataset}`
      )
      this.$store.commit('setCollections', response.data)
    } catch (error) {
      console.log(error)
    }
  }

  @Watch('selections.collection')
  async getSets () {
    this.$store.commit(
      'setSelectedCollection',
      this.$data.selections.collection
    )
    try {
      const response = await axios.get<types.DatasetInfoResponse>(
        `http://127.0.0.1:5000/api/datasets/${this.$data.selections.dataset}`
      )
      this.$store.commit('setSets', response.data)
    } catch (error) {
      console.log(error)
    }
  }

  @Watch('selections.set')
  setSet () {
    this.$store.commit('setSelectedSet', this.$data.selections.set)
  }

  @Watch('selections.set')
  async setShape () {
    try {
      const response = await axios.get<types.ShapeResponse>(
        'http://127.0.0.1:5000/' +
          `api/datasets/${this.$store.state.selectedDataset}/` +
          `${this.$store.state.selectedCollection}/` +
          `${this.$store.state.selectedSet}`
      )
      this.$store.commit('setShape', response.data.data)
    } catch (error) {
      console.log(error)
    }
  }

  @Watch('selections.set')
  async setLabels () {
    try {
      const response = await axios.get<types.LabelsResponse>(
        'http://127.0.0.1:5000/' +
          `api/datasets/${this.$store.state.selectedDataset}/` +
          `${this.$store.state.selectedCollection}/` +
          `${this.$store.state.selectedSet}/labels`
      )
      this.$store.commit('setLabels', response.data.data.labels)
    } catch (error) {
      console.log(error)
    }
  }
}
</script>
