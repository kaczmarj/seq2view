<template>
  <v-card tile>
    <v-container>
      <v-row class="d-flex">
        <v-card-title class="align-center">Nonzero feature values by visit</v-card-title>
        <v-col >
            <v-slider
              label="Visit"
              v-model="visit"
              @change="plot"
              class="align-center"
              :min="1"
              :max="nVisits"
            >
              <template v-slot:append>
                <v-text-field
                  v-model="visit"
                  @change="plot"
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
      <v-row>
        <v-col>
          <div class="d-flex" :id="divID"></div>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import axios from 'axios'
import * as d3 from 'd3'
import * as types from '../types'

@Component
export default class HeatMap extends Vue {
  data () {
    return {
      visit: 1, // 1-based indexing, but API expects 0-based indexing.
      divID: 'heatmap-plot',
      shape: {} as types.Shape
    }
  }

  get nVisits () {
    return this.$store.state.shape.fields.visits
  }

  async getData () {
    const state = this.$store.state
    try {
      const response = await axios.get<types.NonZeroFeatureResponse>(
        'http://127.0.0.1:5000/api/datasets/' +
        `${state.selectedDataset}/${state.selectedCollection}/${state.selectedSet}/${this.$data.visit - 1}`)
      return response.data.data
    } catch (error) {
      console.log(error)
    }
  }

  async plot () {
    const data = await this.getData()
    if (data === undefined) {
      return
    }

    d3.select(`#${this.$data.divID} > svg`).remove()
    const width = 800
    const height = 600
    const margin = { top: 30, right: 30, bottom: 30, left: 30 }

    const svg = d3
      .select(`#${this.$data.divID}`)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')

    // With help from https://www.d3-graph-gallery.com/graph/heatmap_basic.html
    // Add x-axis (time)
    const x = d3
      .scaleBand()
      // https://stackoverflow.com/a/42123984/5666087
      .domain([...new Set(data.features.map(d => d.timepoint.toString()))])
      .range([0, width])
    svg
      .append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(d3.axisBottom(x))

    // Add y-axis (label names)
    const y = d3
      .scaleBand()
      // .domain(data.labels.map(d => d.name))
      .domain(data.features.map(d => d.originalFeatureID.toString()))
      .range([height, 0])
    svg.append('g').call(d3.axisLeft(y))

    // Color scale
    const color = d3
      .scaleLinear<string>()
      .domain(d3.extent(data.features, d => d.value) as [number, number])
      .range(['white', '#E42F2F'])

    svg
      .append('rect')
      .data(data.features)
      .attr('x', d => x(d.timepoint.toString()) as number)
      .attr('y', d => y(d.originalFeatureID.toString()) as number)
      .attr('width', x.bandwidth())
      .attr('height', y.bandwidth())
      .style('fill', d => color(d.value) as string)
  }
}
</script>
