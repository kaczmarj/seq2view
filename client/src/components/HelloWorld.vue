<template>
  <div class="hello">
    <h1>{{ message }}</h1>

    File:
    <select v-model="selectedFile">
      <option v-for="file in files" v-bind:key="file" v-bind:value="file">{{
        file
      }}</option>
    </select>

    <br />

    <input type="radio" id="train" value="train" v-model="trainTest" />
    <label for="train">Train</label>
    <input type="radio" id="test" value="test" v-model="trainTest" />
    <label for="test">Test</label>

    <br />
    Visit:
    <input
      type="range"
      min="0"
      :max="shape.fields.visits"
      step="1"
      v-model="visit"
    />
    <br />
    <input type="number" min="0" :max="shape.fields.visits" v-model="visit" />

    <select v-model="selectedLabel">
      <option
        v-for="label in labels"
        v-bind:key="label.value"
        v-bind:value="label"
        >{{ label.name }}</option
      >
    </select>

    <div id="linePlot"></div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import axios from "axios";
import * as d3 from "d3";

axios.defaults.withCredentials = false;

Vue.config.productionTip = false;

interface FileResponse {
  data: { files: string[] };
  status: string;
}

interface Label {
  value: number;
  name: string;
}

interface LabelResponse {
  data: { labels: Label[] };
  status: string;
}

interface FeaturePoint {
  x: number;
  y: number;
}

interface FeatureResponse {
  data: { label: Label; feature: FeaturePoint[] };
  status: string;
}

interface Shape {
  fields: { [key: string]: number };
  rank: number;
  shape: number[];
}

interface ShapeResponse {
  data: Shape;
  status: string;
}

interface Data {
  files: string[];
  selectedFile: string;
  labels: Label[];
  shape: Shape;
  selectedLabel: Label;
  // TODO: add processed or raw.
  trainTest: "train" | "test";
  visit: number;
}

@Component
export default class HelloWorld extends Vue {
  message = "Plotting component";

  data(): Data {
    return {
      files: [],
      selectedFile: "",
      labels: [],
      shape: {
        fields: { visits: 0, timepoints: 0, features: 0 },
        shape: [0, 0, 0],
        rank: 3
      },
      selectedLabel: { value: 0, name: "unknown" },
      trainTest: "train",
      visit: 0
    };
  }

  get plottingHash(): [string, "train" | "test", number, Label] {
    return [
      this.$data.selectedFile,
      this.$data.trainTest,
      this.$data.visit,
      this.$data.selectedLabel
    ];
  }

  @Watch("plottingHash")
  async plot(sequence: [string, "train" | "test", number, Label]) {
    const file = sequence[0],
      trainTest = sequence[1],
      visit = sequence[2],
      label = sequence[3];

    if (file === "" || label.name === "unknown") {
      return;
    }

    console.log(
      `plotting: file='${file}' trainTest='${trainTest}' visit='${visit}' label='${label.name}'`
    );
    // TODO: check for empty selectedLabel.
    try {
      const response = await axios.get<FeatureResponse>(
        `http://127.0.0.1:5000/api/feature?f=${file}&t=${trainTest}&v=${visit}&i=${label.value}`
      );
      const data = response.data.data.feature;

      d3.select("#linePlot > svg").remove();

      const width = 800,
        height = 200,
        margin = { top: 30, right: 30, bottom: 30, left: 30 };

      const svg = d3
        .select("#linePlot")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      // Add x-axis.
      const x = d3
        .scaleLinear()
        // TODO: how to prevent typescript from thinking value can be undefined?
        .domain(d3.extent(data, d => d.x) as [number, number])
        .range([0, width]);
      svg
        .append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x));

      // Add y-axis
      const y = d3
        .scaleLinear()
        // TODO: how to prevent typescript from thinking value can be undefined?
        .domain(d3.extent(data, d => d.y) as [number, number])
        .range([height, 0]);
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
      const fileResponse = await axios.get<FileResponse>(
        "http://127.0.0.1:5000/api/files"
      );
      this.$data.files = fileResponse.data.data.files;

      const labelResponse = await axios.get<LabelResponse>(
        "http://127.0.0.1:5000/api/labels"
      );
      this.$data.labels = labelResponse.data.data.labels;

      const shapeResponse = await axios.get<ShapeResponse>(
        "http://127.0.0.1:5000/api/features/shape"
      );
      this.$data.shape = shapeResponse.data.data;
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
