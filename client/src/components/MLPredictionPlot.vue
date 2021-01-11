<template>
  <v-container>
    <h2>Plot of model predictions for selection {{ id + 1 }}</h2>
    <div :id="divID"></div>
  </v-container>
</template>

<script lang="ts">
import axios from 'axios'
import * as d3 from 'd3'
import * as types from '../types'
import { Component, Vue, Watch } from 'vue-property-decorator'
import * as _ from 'lodash'

const MLPredictionPlotProps = Vue.extend({
  props: {
    id: Number
  }
})

@Component
export default class MLPredictionPlot extends MLPredictionPlotProps {
  get dataEndpoint () {
    const state = this.$store.state
    const selection: types.FeatureVisitSelection = state.selections[this.id]
    return `api/model/${state.selectedDataset}/${selection.feature.value}`
  }

  get divID () {
    return `multilineplot-${this.id}`
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
      //   state.selectedCollection !== "" &&
      //   state.selectedSet !== "" &&
      //   state.selections[this.id].visit >= 0 &&
      state.selections[this.id].feature.name !== undefined
    )
  }

  @Watch('hash')
  async plot () {
    if (!this.readyToPlot) {
      return
    }

    const response = await axios.get<types.ModelPredictionResponse>(
      `http://127.0.0.1:5000/${this.dataEndpoint}`
    )
    // const data = response.data.data
    const nLines = 10
    const data = response.data.data.filter((d) => d.n < nLines)

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
      .domain(d3.extent(data, (d) => d.h) as [number, number])
      .range([0, width])
    svg
      .append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(d3.axisBottom(x))
    // Add y-axis
    const y = d3
      .scaleLinear()
      // TODO: how to prevent typescript from thinking value can be undefined?
      .domain(d3.extent(data, (d) => d.p) as [number, number])
      .range([height, 0])
    svg.append('g').call(d3.axisLeft(y))

    const groupedData = _.groupBy(data, 'n')
    const groupedDataKeys = _.keys(groupedData)

    for (let i = 0; i < groupedDataKeys.length; i++) {
      const thisKey = groupedDataKeys[i]
      svg
        .append('path')
        .datum(groupedData[thisKey])
        .attr('stroke', 'black')
        .attr('fill', 'none')
        .attr(
          'd',
          d3
            .line<types.ModelPredictionPoint>()
            .x((d) => x(d.h) as number)
            .y((d) => y(d.p) as number)
            .curve(d3.curveBasis)
        )
    }
  }
}
</script>
