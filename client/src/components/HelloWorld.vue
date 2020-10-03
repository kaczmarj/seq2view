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
    <div id="heatmap"></div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import axios from "axios";
import * as d3 from "d3";
import { set } from "vue/types/umd";

axios.defaults.withCredentials = false;

Vue.config.productionTip = false;

type KnownCollections = "raw" | "processed";
type KnownSets = "train" | "test";

// Response of /api/datasets
interface DatasetsResponse {
  data: { datasets: string[] };
  status: string;
}

// Response of /api/datasets/<string:dataset>
interface DatasetInfoResponse {
  data: {
    nodes: {
      collections: { [key: string]: boolean };
      sets: { [key: string]: { [key: string]: boolean } };
    };
  };
  status: string;
}

interface Shape {
  fields: { features: number; timepoints: number; visits: number };
  rank: number;
  shape: [number, number, number];
}

// Response of /api/datasets/<string:dataset>/<string:collection>/<string:set_>
interface ShapeResponse {
  data: Shape;
  status: string;
}

interface Label {
  value: number;
  name: string;
}

// Response of /api/datasets/<string:dataset>/<string:collection>/<string:set_>/labels
interface LabelsResponse {
  data: { labels: Label[] };
  status: string;
}

interface NonZeroVisitDatumFeature {
  featureID: number;
  originalFeatureID: number;
  timepoint: number;
  value: number;
}

interface NonZeroVisitDatumLabel {
  name: string;
  originalValue: number;
  value: number;
}

// Response of "/api/datasets/<string:dataset>/<string:collection>/<string:set_>/<int:visit>
interface NonZeroFeatureResponse {
  data: {
    features: NonZeroVisitDatumFeature[];
    labels: NonZeroVisitDatumLabel[];
  };
  status: string;
}

interface FeaturePoint {
  x: number;
  y: number;
}

// Response of /api/datasets/<string:dataset>/<string:collection>/<string:set_>/<int:visit>/<int:feature>
interface FeatureResponse {
  data: { label: Label; feature: FeaturePoint[] };
  status: string;
}

interface Data {
  datasets: string[];
  selectedDataset: string;
  labels: Label[];
  shape: Shape;
  selectedLabel: Label;
  collection: KnownCollections;
  set: KnownSets;
  visit: number;
}

@Component
export default class HelloWorld extends Vue {
  message = "Plotting component";

  data(): Data {
    return {
      datasets: [],
      selectedDataset: "",
      labels: [],
      shape: {
        fields: { visits: 0, timepoints: 0, features: 0 },
        shape: [0, 0, 0],
        rank: 3
      },
      selectedLabel: { value: 0, name: "unknown" },
      collection: "processed",
      set: "train",
      visit: 0
    };
  }

  get plottingHash(): [string, KnownSets, number, Label] {
    const data = this.$data as Data
    return [
      data.selectedDataset,
      data.set, 
      data.visit,
      data.selectedLabel
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

  @Watch("plottingHash")
  async plotHeatmap(sequence: [string, "train" | "test", number, Label]) {
    const file = sequence[0],
      trainTest = sequence[1],
      visit = sequence[2],
      label = sequence[3];

    if (file === "" || label.name === "unknown") {
      return;
    }

    console.log(
      `plotting heatmap: file='${file}' trainTest='${trainTest}' visit='${visit}'`
    );

    try {
      const response = await axios.get<NonZeroFeatureResponse>(
        `http://127.0.0.1:5000/api/nonzero_features?f=${file}&t=${trainTest}&v=${visit}`
      );
      const data = response.data.data;

      d3.select("#heatmap > svg").remove();

      const width = 800,
        height = 400,
        margin = { top: 30, right: 30, bottom: 30, left: 30 };

      const svg = d3
        .select("#heatmap")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      // Add x-axis (features)
      const x = d3
        .scaleBand()
        .domain(Array.from(data, d => d.feature_id.toString()))
        .range([0, width])
        .padding(0.1);
      svg
        .append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x));

      // Add y-axis (timepoints)
      const y = d3
        .scaleBand()
        // TODO: how to prevent typescript from thinking value can be undefined?
        .domain(Array.from(data, d => d.timepoint.toString()))
        .range([height, 0])
        .padding(0.1);
      svg.append("g").call(d3.axisLeft(y));

      const color = d3
        .scaleLinear<string>()
        .range(["black", "blue"])
        .domain(d3.extent(data, d => d.value));

      console.log(`extent: ${d3.extent(data, d => d.value)}`);

      svg
        .data(data)
        .enter()
        .append("rect")
        .attr("x", d => x(d.feature_id.toString()))
        .attr("y", d => y(d.timepoint.toString()))
        .attr("width", x.bandwidth())
        .attr("height", y.bandwidth())
        .style("fill", d => color(d.value));
    } catch (error) {
      console.log(error);
    }
  }

  async mounted() {
    try {
      const fileResponse = await axios.get<DatasetsResponse>(
        "http://127.0.0.1:5000/api/files"
      );
      this.$data.files = fileResponse.data.data.datasets;

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
