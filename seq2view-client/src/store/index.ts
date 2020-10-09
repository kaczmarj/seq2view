// The one true source of information.

import Vue from 'vue'
import Vuex from 'vuex'
import * as types from '../types'

Vue.use(Vuex)

export const store = new Vuex.Store({
  state: {
    datasets: [] as string[],
    collections: [] as types.KnownCollections[],
    sets: [] as types.KnownSets[],
    selectedDataset: '',
    selectedCollection: '' as types.KnownCollections,
    selectedSet: '' as types.KnownSets,
    shape: {
      fields: { features: 0, timepoints: 0, visits: 0 },
      rank: 0,
      shape: [0, 0, 0]
    } as types.Shape,
    labels: [] as types.Label[],
    selections: [{ id: 0, feature: '', visit: 0 }] as types.FeatureVisitSelection[],
    showDrawer: true
  },
  mutations: {

    setDatasets (state, datasets: types.DatasetsResponse) {
      state.datasets = datasets.data.datasets
    },

    setCollections (state, info: types.DatasetInfoResponse) {
      const c = info.data.nodes.collections
      state.collections = Object.keys(c).filter(d => c[d]) as types.KnownCollections[]
    },

    setSets (state, info: types.DatasetInfoResponse) {
      const sets = info.data.nodes.sets
      const selectedCollection = state.selectedCollection
      state.sets = Object
        .keys(sets[selectedCollection])
        .filter(k => sets[selectedCollection][k]) as types.KnownSets[]
    },

    setSelectedDataset (state, dataset: string) {
      state.selectedDataset = dataset
    },

    setSelectedCollection (state, collection: types.KnownCollections) {
      state.selectedCollection = collection
    },

    setSelectedSet (state, set: types.KnownSets) {
      state.selectedSet = set
    },

    setShape (state, shape: types.Shape) {
      state.shape = shape
    },

    setLabels (state, labels: types.Label[]) {
      state.labels = labels
    },

    addSelection (state) {
      let lastID = 0
      if (state.selections.length > 0) {
        lastID = state.selections[state.selections.length - 1].id
      }
      state.selections.push({
        id: lastID + 1,
        feature: '',
        visit: 0
      })
    },

    popSelection (state) {
      state.selections.pop()
    },

    updateSelection (state, kwargs: {id: number; feature: string; visit: number}) {
      state.selections[kwargs.id].feature = kwargs.feature
      state.selections[kwargs.id].visit = kwargs.visit
    },

    invertShowDrawer (state) {
      state.showDrawer = !state.showDrawer
    }
  },
  actions: {
  },
  modules: {
  }
})
