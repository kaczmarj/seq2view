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
      selectedLabel: {},
      plottingData: [] as { value: number; index: number }[]
    };
  }

  async plot() {
    // TODO: check for empty selectedLabel.
    try {
      const response = await axios.get<FeatureResponse>(
        `http://127.0.0.1:5000/api/todo?day=${this.$data.selectedLabel}`
      );
      this.$data.plottingData = response.data.data.feature;
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
