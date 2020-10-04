<template>
  <v-app id="inspire">
        <v-app-bar clipped-left app>
          <v-app-bar-nav-icon @click="invertShowDrawer"></v-app-bar-nav-icon>
      <!-- <v-app-bar-nav-icon @click="showDrawer = !showDrawer"></v-app-bar-nav-icon> -->
      <v-toolbar-title>Data Viewer</v-toolbar-title>
      <v-spacer></v-spacer>
       <v-btn class="ma-2" href="https://github.com/kaczmarj/seq2view" target="_blank">
        <v-icon left>mdi-github</v-icon>
        Source
      </v-btn>

    </v-app-bar>

    <Drawer  />
    <v-main>
      <Plots />
    </v-main>
  </v-app>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import Plots from '@/components/Plots.vue'
import Drawer from '@/components/Drawer.vue'
@Component({
  components: {
    Drawer,
    Plots
  }
})
export default class App extends Vue {
  data () {
    return {}
  }

  invertShowDrawer () {
    this.$store.commit('invertShowDrawer')
  }
}
</script>
