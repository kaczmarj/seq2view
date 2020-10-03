<template>
  <v-container>
    <v-row class="text-center grey">

      <v-col class="mb-4 green">
        <h1 class="display-2 font-weight-bold mb-3">
          Plots go here
        </h1>
      </v-col>

    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class Plots extends Vue {
  data () {
    return {
    }
  }
}
</script>
