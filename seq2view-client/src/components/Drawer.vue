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

        <v-row>
            <v-col>
                <VisitLabelSelector selection="Selection 1" />
            </v-col>
        </v-row>

        <v-row>
            <v-col>
                <VisitLabelSelector selection="Selection 2" />
            </v-col>
        </v-row>

        </v-container>
    </v-navigation-drawer>

</template>

<script lang="ts">
import DatasetSubsetSelector from '@/components/DatasetSubsetSelector.vue'
import VisitLabelSelector from '@/components/VisitLabelSelector.vue'
import { Component, Vue } from 'vue-property-decorator'

@Component({ components: { DatasetSubsetSelector, VisitLabelSelector } })
export default class Drawer extends Vue {
  data () {
    return {
      show: true
    }
  }
}
</script>
