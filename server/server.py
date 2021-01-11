"""
Flask application to serve data in JSON API. Only GET requests are implemented.
"""

import functools
import itertools
import json
import os
import pathlib

import fastapi
from fastapi.middleware.cors import CORSMiddleware
import h5py
import numpy as np

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _get_registered_datasets(log=True):
    datasets = {}
    for key in os.environ.keys():
        if key.startswith("SEQ2VIEW_DATASET_"):
            k = key.split("_")[2]
            filepath = os.environ[key]
            if not os.path.exists(filepath):
                raise FileNotFoundError(filepath)
            datasets[k] = filepath

    if not datasets:
        raise ValueError("no datasets registered")

    if log:
        print("registered datasets:")
        for k, v in datasets.items():
            print(f"  {k} = {v}")

    return datasets


_datasets = _get_registered_datasets(log=True)


@app.get("/api/datasets")
async def get_datasets():
    return {"data": {"datasets": list(_datasets.keys())}}


@app.get("/api/datasets/{dataset}")
async def get_dataset_info(dataset: str):
    dataset = _get_dataset(dataset)
    return {
        "data": {"nodes": {"collections": dataset.collections, "sets": dataset.sets}}
    }


@app.get("/api/datasets/{dataset}/{collection}/{set_}")
async def get_shape(dataset: str, collection: str, set_: str):
    dataset = _get_dataset(dataset)
    shape = dataset.shape(collection=collection, set_=set_)
    rank = len(shape)
    if rank != 3:
        raise fastapi.HTTPException(
            500, detail=f"expected data of rank 3 but got {rank}"
        )
    return {
        "data": {
            "shape": shape,
            "rank": rank,
            "fields": {
                "visits": shape[0],
                "timepoints": shape[1],
                "features": shape[2],
            },
        },
    }


@app.get("/api/datasets/{dataset}/{collection}/{set_}/labels")
async def get_labels(dataset: str, collection: str, set_: str):
    dataset = _get_dataset(dataset)
    try:
        labels = dataset.human_readable_labels(collection=collection, set_=set_)
        return {
            "data": {
                "labels": [
                    {"value": j, "name": label} for j, label in enumerate(labels)
                ]
            },
        }
    except NodeNotFound as e:
        raise fastapi.HTTPException(400, detail=str(e))


@app.get("/api/datasets/{dataset}/{collection}/{set_}/{visit}")
async def get_nonzero_visit_data(dataset: str, collection: str, set_: str, visit: int):
    dataset = _get_dataset(dataset)
    try:
        (
            nonzero_visit_data,
            original_feature_ids,
            labels_included,
        ) = dataset.nonzero_visit_data(collection=collection, set_=set_, visit=visit)

        features = []
        for i, j in itertools.product(
            range(nonzero_visit_data.shape[0]), range(nonzero_visit_data.shape[1])
        ):
            d = {
                "timepoint": i,
                "featureID": j,
                "originalFeatureID": original_feature_ids[j],
                "value": nonzero_visit_data[i, j],
            }
            features.append(d)

        labels = [
            {"value": j, "originalValue": orig, "name": label}
            for j, (orig, label) in enumerate(
                zip(original_feature_ids, labels_included)
            )
        ]

        return {
            "data": {"labels": labels, "features": features},
        }

    except (KeyError, ValueError) as e:
        raise fastapi.HTTPException(400, detail=str(e))


@app.get("/api/datasets/{dataset}/{collection}/{set_}/{visit}/{feature}")
async def get_feature(
    dataset: str, collection: str, set_: str, visit: int, feature: int
):
    dataset = _get_dataset(dataset)

    try:
        x, y = dataset.features(
            collection=collection, set_=set_, visit=visit, feature=feature
        )
        feature_labels = dataset.human_readable_labels(collection=collection, set_=set_)
        human_readable_label = feature_labels[feature]
        return {
            "data": {
                "feature": [{"x": i, "y": j} for (i, j) in zip(x, y)],
                "label": {"value": feature, "name": human_readable_label},
            },
        }
    except (KeyError, ValueError) as e:
        raise fastapi.HTTPException(400, detail=str(e))


class NodeNotFound(Exception):
    """Node does not exist in dataset."""

    pass


class HDF5Dataset:
    """Object to interact with HDF5 file.

    Parameters
    ----------
    filepath : str, Path-like
        Path to HDF5 file containing data.

    Notes
    -----
    Collection is defined as raw or processed. Set is defined as
    the train, validation, or test set. In the implementation below,
    `set_` is used to avoid shadowing the builtin `set`.
    """

    def __init__(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"file not found: {filepath}")
        self._filepath = filepath
        # HDF5 node names are POSIX-like.
        self._root_node = pathlib.PosixPath("/data")

    def _raise_if_node_not_found(self, node):
        node = str(node)
        with h5py.File(self._filepath, mode="r") as f:
            if node not in f:
                raise NodeNotFound(f"node not found: {node}")

    @functools.cached_property
    def collections(self):
        d = {}
        with h5py.File(self._filepath, mode="r") as f:
            for collection in {"processed", "raw"}:
                node = self._root_node / collection
                d[collection] = str(node) in f
        return d

    @functools.cached_property
    def sets(self):
        d = {k: {} for k in self.collections.keys()}
        with h5py.File(self._filepath, mode="r") as f:
            for set_ in {"train", "test"}:
                for collection in self.collections.keys():
                    node = self._root_node / collection / set_
                    d[collection][set_] = str(node) in f
        return d

    def shape(self, collection="processed", set_="train"):
        node = self._root_node / collection / set_ / "sequence" / "core_array"
        self._raise_if_node_not_found(node)
        with h5py.File(self._filepath, mode="r") as f:
            return f[str(node)].shape

    def human_readable_labels(self, collection="processed", set_="train"):
        node = self._root_node / collection / set_ / "target" / "column_annotations"
        self._raise_if_node_not_found(node)
        with h5py.File(self._filepath, mode="r") as f:
            labels = f[str(node)][:].flatten().tolist()
        return [label.decode() for label in labels]

    def features(self, collection="processed", set_="train", visit=None, feature=None):
        node = self._root_node / collection / set_ / "sequence" / "core_array"
        self._raise_if_node_not_found(node)
        with h5py.File(self._filepath, mode="r") as f:
            shape = f[str(node)].shape
            # Could use the := (walrus) operator here, but that requires python>=3.8.
            if ndim := len(shape) != 3:
                raise ValueError(f"expected 3D array but got {ndim}D")
            n_visits, _, n_features = shape
            if visit is not None:
                if visit < 0 or visit >= n_visits:
                    raise ValueError(
                        f"'visit' must be in [0, {n_visits}) but got {visit}"
                    )
            else:
                visit = slice(None)
            if feature is not None:
                if feature < 0 or feature >= n_features:
                    raise ValueError(
                        f"'feature' must be in [0, {n_features}) but got {feature}"
                    )
            else:
                feature = slice(None)

            x = f[str(node)][visit, :, -1]  # time
            y = f[str(node)][visit, :, feature]  # values

        # TODO: add this back in when using non-synthetic data.
        # Remove NaN values and samples where x and y are zero.
        bad_indices = np.isnan(x) | np.isnan(y) | ((x == 0) & (y == 0))
        x = x[~bad_indices].astype(float)
        y = y[~bad_indices].astype(float)

        return x.astype(float), y.astype(float)

    def nonzero_visit_data(self, visit, collection="processed", set_="train"):
        """Return tuple of features, original feature IDs, and
        human-readable labels where the feature data is not 0.
        """
        _, visit_data = self.features(visit=visit, collection=collection, set_=set_)
        feature_mask = visit_data.any(axis=0)
        nonzero_visit_data = visit_data[:, feature_mask]
        original_feature_ids = np.argwhere(feature_mask).flatten()
        labels = np.asarray(
            self.human_readable_labels(collection=collection, set_=set_)
        )
        if feature_mask.shape[0] != labels.shape[0]:
            m = "number of data points kept does not match number of human readable labels kept."
            raise ValueError(m)
        labels_included = labels[feature_mask]
        return (
            nonzero_visit_data,
            original_feature_ids.tolist(),
            labels_included.tolist(),
        )


def _get_dataset(dataset: str) -> HDF5Dataset:
    try:
        filepath = _datasets[dataset]
    except KeyError:
        raise fastapi.HTTPException(status_code=404, detail="unknown dataset")
    try:
        return HDF5Dataset(filepath)
    except FileNotFoundError:
        raise fastapi.HTTPException(status_code=500, detail="dataset file not found")


################################
# Machine learning bits below  #
################################


@app.get("/api/model/{dataset}/{feature}")
def get_predictions_by_timepoint_test(dataset: str, feature: int):
    """Function used for debugging. Returns pre-made results."""
    import json

    with open("sample-data.json", "r") as f:
        d = json.load(f)

    return d


def get_predictions_by_timepoint(data_path, model_path, model_summary_path):

    import pandas as pd
    import tensorflow as tf

    with h5py.File(data_path, "r") as f:
        x_ref_raw = f["/data/processed/test/raw_sequence/core_array"][:]
        x_ref = f["/data/processed/test/sequence/core_array"][:]
        y_ref = f["/data/processed/test/target/core_array"][:]
        identifiers = f["/data/processed/test/identifiers/core_array"][:]
        target_labels = (
            f["/data/processed/train/target/column_annotations"][:].ravel().tolist()
        )
        identifier_labels = (
            f["/data/processed/test/identifiers/column_annotations"][:].ravel().tolist()
        )

    with open(model_summary_path) as f:
        model_summary = json.load(f)

    model = tf.keras.models.load_model(model_path, compile=False)
    y_pred = tf.math.sigmoid(model.predict(x_ref).ravel()).numpy()

    pred_indices_high_to_low = np.argsort(y_pred)[::-1]

    identifiers = identifiers[pred_indices_high_to_low]
    y_pred_sorted = y_pred[pred_indices_high_to_low]

    target_label = model_summary["target"]["target_name"]
    target_labels = [str(s, "utf-8") for s in target_labels]
    target_label_index = target_labels.index(target_label)

    identifier_labels = [str(s, "utf-8") for s in identifier_labels]
    y_ref_target_sorted = y_ref[:, target_label_index][pred_indices_high_to_low]

    # TODO: is it necessary to make this dataframe? We don't use much of it...
    # create (n_timepoints, 6) shape DataFrame.
    three_cols = np.stack(
        [pred_indices_high_to_low, y_pred_sorted, y_ref_target_sorted], axis=1
    )
    data = np.concatenate((identifiers, three_cols), axis=1)
    columns = [
        "id",
        "identifier_id",
        "start_time",
        "position",
        "probability",
        "ground_truth",
    ]
    df = pd.DataFrame(data, columns=columns)
    df = df.astype(
        {
            "id": int,
            "identifier_id": int,
            "start_time": int,
            "position": int,
            "probability": float,
            "ground_truth": int,
        }
    )

    top_n = sum(df["probability"] >= 0.5)
    position_index = df.position.iloc[:top_n].to_numpy()

    _, n_time_steps, n_features = x_ref.shape  # is the first item n_visits?

    # Uses sequence, not raw_sequence.
    hour_arrays = x_ref_raw[position_index, :, -1]

    sequence_end_array = (hour_arrays != 0).argmin(axis=1)
    sequence_end_array[sequence_end_array == 0] = n_time_steps - 1

    # Predicting by timepoint.
    p = tf.keras.utils.Progbar(n_time_steps)
    tmp = x_ref[position_index[:top_n]]
    tmpzero = np.zeros_like(tmp)
    preds_by_timestep = np.zeros((top_n, n_time_steps))
    # Predict `n_time_steps` times, each iteration adding a new datapoint.
    # This way, we can see how well we predict knowing all the information up to a certain point.
    for timestep in range(n_time_steps):
        tmpzero[:, timestep] = tmp[:, timestep]
        preds_by_timestep[:, timestep] = tf.sigmoid(
            model.predict(tmpzero).ravel()
        ).numpy()
        p.add(1)

    d = {"data": []}
    for i in range(top_n):
        end = sequence_end_array[i]
        hs = hour_arrays[i, :end]
        ps = preds_by_timestep[i, :end]
        d["data"].extend(
            [{"h": h.item(), "p": p.item(), "n": i} for (h, p) in zip(hs, ps)]
        )

    d["n_items"] = len(d["data"])

    return d
