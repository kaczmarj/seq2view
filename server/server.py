"""
Flask application to serve data in JSON API. Only GET requests are implemented.
"""

import itertools
import os
from pathlib import Path
from pathlib import PosixPath

import flask
import flask_cors
import h5py
import numpy as np

# JSend spec https://github.com/omniti-labs/jsend
STATUS_SUCCESS = "success"
STATUS_FAIL = "fail"
STATUS_ERROR = "error"

app = flask.Flask(__name__)
flask_cors.CORS(app)  # TODO: remove for production. Enable CORS during development.

# Attempt to mock having filepaths stored somewhere and referenced in API.
_datasets = {"0001": Path(__file__).parent / "processed_ohdsi_sequences.h5"}

@app.route("/api/files", methods=["GET"])
def get_files():
    return  {
        "data": {"files": list(_datasets.keys())}
}

@app.route("/api/labels", methods=["GET"])
def get_labels():
    filepath = _datasets["0001"]
    dataset = HDF5Dataset(filepath)
    # subset="processed", train_test="train"
    labels = dataset.human_readable_labels()
    return {
        "status": STATUS_SUCCESS,
        "data": {
            "labels": [{"value": j, "name": label} for j, label in enumerate(labels)]
        },
    }


@app.route("/api/features/shape", methods=["GET"])
def get_shape():
    file_id = flask.request.args.get("f", default="0001", type=str)
    subset = flask.request.args.get("s", default="processed", type=str)
    train_test = flask.request.args.get("t", default="train", type=str)

    try:
        filepath = _datasets[file_id]
    except KeyError:
        return {
            "status": STATUS_FAIL,
            "data": {"message": "dataset not found"}
        }
    dataset = HDF5Dataset(filepath)
    # subset="processed", train_test="train"
    shape = dataset.shape()
    if len(shape) != 3:
        raise ValueError(f"Expected rank 3 but got {len(shape)}")
    return {
        "status": STATUS_SUCCESS,
        "data": {
            "shape": shape,
            "rank": len(shape),
            "fields": {
            "visits": shape[0],
            "timepoints": shape[1],
            "features": shape[2],}
        },
    }

@app.route("/api/feature", methods=["GET"])
def get_feature():
    file_id = flask.request.args.get("f", default="0001", type=str)
    subset = flask.request.args.get("s", default="processed", type=str)
    train_test = flask.request.args.get("t", default=None, type=str)
    visit = flask.request.args.get("v", default=None, type=int)
    feature_idx = flask.request.args.get("i", default=None, type=int)

    try:
        filepath = _datasets[file_id]
    except KeyError:
        return {
            "status": STATUS_FAIL,
            "data": {"message": "dataset not found"}
        }
    if visit is None:
        return {
            "status": STATUS_FAIL,
            "data": {"message": "missing required argument 'v' for visit"},
        }
    if feature_idx is None:
        return {
            "status": STATUS_FAIL,
            "data": {"message": "missing required argument 'i' for feature index"},
        }
    if train_test is None:
        return {
            "status": STATUS_FAIL,
            "data": {"message": "missing required argument 't' for train/test"},
        }

    filepath = _datasets["0001"]
    dataset = HDF5Dataset(filepath)

    try:
        x, y = dataset.feature(
            subset="processed", train_test=train_test, visit=visit, feature=feature_idx
        )
        feature_labels = dataset.human_readable_labels()
        human_readable_label = feature_labels[feature_idx]
        return {
            "status": STATUS_SUCCESS,
            "data": {
                "feature": [{"x": i, "y": j} for (i, j) in zip(x, y)],
                "label": {"value": feature_idx, "name": human_readable_label},
            },
        }
    except (KeyError, ValueError) as err:
        return {"status": STATUS_FAIL, "data": {"error": {"message": str(err)}}}


@app.route("/api/nonzero_features", methods=["GET"])
def get_nonzero_features():
    file_id = flask.request.args.get("f", default="0001", type=str)
    subset = flask.request.args.get("s", default="processed", type=str)
    train_test = flask.request.args.get("t", default=None, type=str)
    visit = flask.request.args.get("v", default=None, type=int)
    feature_idx = flask.request.args.get("i", default=None, type=int)

    try:
        filepath = _datasets[file_id]
    except KeyError:
        return {
            "status": STATUS_FAIL,
            "data": {"message": "dataset not found"}
        }
    if visit is None:
        return {
            "status": STATUS_FAIL,
            "data": {"message": "missing required argument 'v' for visit"},
        }
    if train_test is None:
        return {
            "status": STATUS_FAIL,
            "data": {"message": "missing required argument 't' for train/test"},
        }

    filepath = _datasets["0001"]
    dataset = HDF5Dataset(filepath)

    try:
        nonzero_visit_data, original_feature_ids, labels_included = dataset.get_nonzero_visit_data(
            subset="processed", train_test=train_test, visit=visit
        )

        data = []
        for i, j in itertools.product(range(nonzero_visit_data.shape[0]), range(nonzero_visit_data.shape[1])):
            d = {"timepoint": i, "feature_id": j, "original_feature_id": original_feature_ids[j], "value": nonzero_visit_data[i, j]}
            data.append(d)
        return {
            "status": STATUS_SUCCESS,
            "data": data
        }
    except (KeyError, ValueError) as err:
        return {"status": STATUS_FAIL, "data": {"error": {"message": str(err)}}}


class HDF5Dataset:
    """Object to interact with HDF5 file.

    Parameters
    ----------
    filepath : str, Path-like
        Path to HDF5 file containing data.
    """

    def __init__(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"file not found: {filepath}")
        self._filepath = filepath
        # HDF5 node names are POSIX-like.
        self._root_node = PosixPath("/data")

    def shape(self, subset="processed", train_test="train"):
        node = self._root_node / subset / train_test / "sequence" / "core_array"
        with h5py.File(self._filepath, mode="r") as f:
            return f[str(node)].shape

    def human_readable_labels(self, subset="processed", train_test="train"):
        node = self._root_node / subset / train_test / "sequence" / "column_annotations"
        with h5py.File(self._filepath, mode="r") as f:
            labels = f[str(node)][:].flatten().tolist()
        return [label.decode() for label in labels]

    def feature(self, subset="processed", train_test="train", visit=None, feature=None):
        node = self._root_node / subset / train_test / "sequence" / "core_array"
        with h5py.File(self._filepath, mode="r") as f:
            shape = f[str(node)].shape
            # Could use the := (walrus) operator here, but that requires python>=3.8.
            if len(shape) != 3:
                raise ValueError(f"expected rank 3 array but got rank {len(shape)}")
            n_visits, n_timepoints, n_features = shape
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

            x = f[str(node)][visit, :, -1]
            y = f[str(node)][visit, :, feature]

        # TODO: add this back in when using non-synthetic data.
        # Remove NaN values and samples where x and y are zero.
        # bad_indices = np.isnan(x) | np.isnan(y) | ((x == 0) & (y == 0))
        # x = x[~bad_indices].astype(float)
        # y = y[~bad_indices].astype(float)

        return x.astype(float), y.astype(float)

    def get_nonzero_visit_data(self, visit, subset="processed", train_test="train"):
        """Return array of features and human-readable labels where the feature data is not 0.
        """
        _, visit_data = self.feature(visit=visit, subset=subset, train_test=train_test)
        feature_mask = visit_data.any(axis=0)
        nonzero_visit_data = visit_data[:, feature_mask]
        original_feature_ids = np.argwhere(feature_mask).flatten().astype(float)
        labels = np.asarray(self.human_readable_labels(subset=subset, train_test=train_test))
        if feature_mask.shape[0] != labels.shape[0]:
            m = "number of data points kept does not match number of human readable labels kept."
            raise ValueError(m)
        labels_included = labels[feature_mask]
        return nonzero_visit_data, original_feature_ids, labels_included
