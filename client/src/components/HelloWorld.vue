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
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import axios from "axios";
// import * as d3 from "d3";

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

  async plot() {
    // TODO: check for empty selectedLabel.
    try {
      const response = await axios.get<FeatureResponse>(
        `http://127.0.0.1:5000/api/feature?label=${this.$data.selectedLabel.value}`
      );
      const data = response.data.data.feature;

      // create svg element:
      // var svg = d3
      //   .select("#line")
      //   .append("svg")
      //   .attr("width", 800)
      //   .attr("height", 200);

      // // prepare a helper function
      // var lineFunc = d3
      //   .line()
      //   .x(function(d) {
      //     return d.x;
      //   })
      //   .y(function(d) {
      //     return d.y;
      //   });

      // // Add the path using this helper function
      // svg
      //   .append("path")
      //   .attr("d", lineFunc(data))
      //   .attr("stroke", "black")
      //   .attr("fill", "none");
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
