<template>
  <v-container>
    <h2>Plot for selection {{ id + 1 }}</h2>
    <div :id="divID"></div>
  </v-container>
</template>

<script lang="ts">
import axios from 'axios'
import * as d3 from 'd3'
import * as types from '../types'
import { Component, Vue, Watch } from 'vue-property-decorator'

const LinePlotProps = Vue.extend({
  props: {
    id: Number
  }
})

@Component
export default class LinePlot extends LinePlotProps {
  get dataEndpoint () {
    const state = this.$store.state
    const selection: types.FeatureVisitSelection = state.selections[this.id]
    return (
      '/api/datasets/' +
      `${state.selectedDataset}/` +
      `${state.selectedCollection}/` +
      `${state.selectedSet}/` +
      `${selection.visit}/` +
      `${selection.feature.value}`
    )
  }

  get divID () {
    return `lineplot-${this.id}`
  }

  get hash () {
    const state = this.$store.state
    return [
      state.selectedDataset,
      state.selectedCollection,
      state.selectedSet,
      state.selections[this.id].visit,
      state.selections[this.id].feature.value
    ]
  }

  get readyToPlot () {
    const state = this.$store.state
    return (
      state.selectedDataset !== '' &&
      state.selectedCollection !== '' &&
      state.selectedSet !== '' &&
      state.selections[this.id].visit >= 0 &&
      state.selections[this.id].feature.name !== undefined
    )
  }

  @Watch('hash')
  async plot () {
    if (!this.readyToPlot) {
      return
    }

    const response = await axios.get<types.FeatureResponse>(
      `http://127.0.0.1:5000/${this.dataEndpoint}`
    )
    const data = response.data.data.feature
    d3.select(`#${this.divID} > svg`).remove()
    const width = 800
    const height = 200
    const margin = { top: 30, right: 30, bottom: 30, left: 30 }

    const svg = d3
      .select(`#${this.divID}`)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
    // Add x-axis.
    const x = d3
      .scaleLinear()
      // TODO: how to prevent typescript from thinking value can be undefined?
      .domain(d3.extent(data, (d) => d.x) as [number, number])
      .range([0, width])
    svg
      .append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(d3.axisBottom(x))
    // Add y-axis
    const y = d3
      .scaleLinear()
      // TODO: how to prevent typescript from thinking value can be undefined?
      .domain(d3.extent(data, (d) => d.y) as [number, number])
      .range([height, 0])
    svg.append('g').call(d3.axisLeft(y))
    svg
      .append('path')
      .datum(data)
      .attr('stroke', 'black')
      .attr('fill', 'none')
      .attr(
        'd',
        d3
          .line<types.FeaturePoint>()
          .x((d) => x(d.x) as number)
          .y((d) => y(d.y) as number)
          .curve(d3.curveBasis)
      )
  }
}
</script>
