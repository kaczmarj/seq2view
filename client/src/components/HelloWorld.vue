<template>
  <div class="hello">
    <h1>{{ message }}</h1>

    <p>
      Selected label:
      <span
        v-if="typeof(selectedLabel.name) !== 'undefined'"
      >{{ selectedLabel.name }} ({{ selectedLabel.value }})</span>
    </p>
    <select v-model="selectedLabel">
      <option selected disabled hidden>Please choose one</option>
      <option v-for="label in labels" v-bind:key="label.value" v-bind:value="label">{{ label.name }}</option>
    </select>

    <div id="line"></div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import axios from "axios";
import * as d3 from "d3";

axios.defaults.withCredentials = false;

Vue.config.productionTip = false;

interface Label {
  value: number;
  name: string;
}

interface LabelResponse {
  data: { labels: Label[] };
}

interface FeaturePoint {
  x: number;
  y: number;
}

interface FeatureResponse {
  data: { label: Label; feature: FeaturePoint[] };
}

@Component
export default class HelloWorld extends Vue {
  message = "Example data component";

  data() {
    return {
      labels: [] as Label[],
      selectedLabel: {} as Label
      // plottingData: [] as FeaturePoint[]
    };
  }

  @Watch("selectedLabel")
  async plot(label: Label) {
    console.log(`Plotting data for label '${label.name}'`);
    // TODO: check for empty selectedLabel.
    try {
      const response = await axios.get<FeatureResponse>(
        `http://127.0.0.1:5000/api/feature?label=${label.value}`
      );
      const data = response.data.data.feature;

      console.log(data);

      d3.select("#line svg").remove();
      const svg = d3
        .select("#line")
        .append("svg")
        .attr("width", 800)
        .attr("height", 200);

      // Add x-axis.
      const x = d3
        .scaleLinear()
        // TODO: how to prevent typescript from thinking value can be undefined?
        .domain(d3.extent(data, d => d.x) as [number, number])
        .range([0, +svg.attr("width")]);
      svg
        .append("g")
        .attr("transform", `translate(0, ${svg.attr("height")})`)
        .call(d3.axisBottom(x));

      // Add y-axis
      const y = d3
        .scaleLinear()
        // TODO: how to prevent typescript from thinking value can be undefined?
        .domain(d3.extent(data, d => d.y) as [number, number])
        .range([+svg.attr("height"), 0]);
      svg.append("g").call(d3.axisLeft(y));

      svg
        .append("path")
        .datum(data)
        .attr("stroke", "black")
        .attr("fill", "none")

        .attr(
          "d",
          d3
            .line<FeaturePoint>()
            .x(d => x(d.x))
            .y(d => y(d.y))
            .curve(d3.curveBasis) as any // TODO: figure out how to avoid `as any`.
        );
    } catch (error) {
      console.log(error);
    }
  }

  async mounted() {
    try {
      const response = await axios.get<LabelResponse>(
        "http://127.0.0.1:5000/api/labels"
      );
      this.$data.labels = response.data.data.labels;
    } catch (error) {
      console.log(error);
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
