<template>
     <v-navigation-drawer
      app
      v-model="show"
      clipped
      hide-overlay
      stateless
    >
        <v-container class="pa-0">

        <v-row>
            <v-col>
                <DatasetSubsetSelector />
            </v-col>
        </v-row>
        <v-row v-for="(selector, index) in visitLabelSelectors" :key="index">
            <v-col>
                <VisitLabelSelector :selection="`Selection ${index+1}`" />
            </v-col>
        </v-row>

        <v-row>
            <v-col align="center">
        <v-btn
            elevation="2"
            color="success"
            @click="addVisitLabelSelector"
            >Add</v-btn>
            </v-col>
            <v-col>
        <v-btn
            elevation="2"
            color="error"
            :disabled="visitLabelSelectors.length===0"
            @click="popVisitLabelSelector"
            >Remove</v-btn>
            </v-col>
        </v-row>

        </v-container>
    </v-navigation-drawer>

</template>

<script lang="ts">
import DatasetSubsetSelector from '@/components/DatasetSubsetSelector.vue'
import VisitLabelSelector from '@/components/VisitLabelSelector.vue'
import { Selection } from '../store/index'
import { Component, Vue } from 'vue-property-decorator'

@Component({ components: { DatasetSubsetSelector, VisitLabelSelector } })
export default class Drawer extends Vue {
  data () {
    return {
      show: true
    }
  }

  get visitLabelSelectors (): Selection[] {
    return this.$store.state.selections
  }

  addVisitLabelSelector () {
    this.$store.commit('addSelection')
  }

  popVisitLabelSelector () {
    this.$store.commit('popSelection')
  }
}
</script>
