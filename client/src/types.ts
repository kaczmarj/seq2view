export type KnownCollections = 'raw' | 'processed';
export type KnownSets = 'train' | 'test';

// Response of /api/datasets
export interface DatasetsResponse {
  data: { datasets: string[] };
}

// Response of /api/datasets/<string:dataset>
export interface DatasetInfoResponse {
  data: {
    nodes: {
      collections: { [key: string]: boolean };
      sets: { [key: string]: { [key: string]: boolean } };
    };
  };
}

export interface Shape {
  fields: { features: number; timepoints: number; visits: number };
  rank: number;
  shape: [number, number, number];
}

// Response of /api/datasets/<string:dataset>/<string:collection>/<string:set_>
export interface ShapeResponse {
  data: Shape;
}

export interface Label {
  value: number;
  name: string;
}

// Response of /api/datasets/<string:dataset>/<string:collection>/<string:set_>/labels
export interface LabelsResponse {
  data: { labels: Label[] };
}

export interface NonZeroVisitDatumFeature {
  featureID: number;
  originalFeatureID: number;
  timepoint: number;
  value: number;
}

export interface NonZeroVisitDatumLabel {
  name: string;
  originalValue: number;
  value: number;
}

// Response of "/api/datasets/<string:dataset>/<string:collection>/<string:set_>/<int:visit>
export interface NonZeroFeatureResponse {
  data: {
    features: NonZeroVisitDatumFeature[];
    labels: NonZeroVisitDatumLabel[];
  };
}

export interface FeaturePoint {
  x: number;
  y: number;
}

// Response of /api/datasets/<string:dataset>/<string:collection>/<string:set_>/<int:visit>/<int:feature>
export interface FeatureResponse {
  data: { label: Label; feature: FeaturePoint[] };
}

// Selection of feature and visit.
export interface FeatureVisitSelection {
  id: number;
  feature: Label;
  visit: number;
}

export interface ModelPredictionPoint {
  h: number; p: number; n: number
}

// Response of /api/model/<string:dataset>/<int:feature>
export interface ModelPredictionResponse {
  data: ModelPredictionPoint[];
  n_items: number;
}
