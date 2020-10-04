export type KnownCollections = 'raw' | 'processed';
export type KnownSets = 'train' | 'test';

// Response of /api/datasets
export interface DatasetsResponse {
  data: { datasets: string[] };
  status: string;
}
// Response of /api/datasets/<string:dataset>
export interface DatasetInfoResponse {
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
export interface ShapeResponse {
  data: Shape;
  status: string;
}
interface Label {
  value: number;
  name: string;
}
// Response of /api/datasets/<string:dataset>/<string:collection>/<string:set_>/labels
export interface LabelsResponse {
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
export interface NonZeroFeatureResponse {
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
export interface FeatureResponse {
  data: { label: Label; feature: FeaturePoint[] };
  status: string;
}
