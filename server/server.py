"""
Flask application to serve data in JSON API. Only GET requests are implemented.
"""

import os
from pathlib import Path, PosixPath

import flask
import flask_cors
import h5py

# JSend spec https://github.com/omniti-labs/jsend
STATUS_SUCCESS = "success"
STATUS_FAIL = "fail"
STATUS_ERROR = "error"

app = flask.Flask(__name__)
flask_cors.CORS(app)  # TODO: remove for production. Enable CORS during development.

# Attempt to mock having filepaths stored somewhere and referenced in API.
_datasets = {"0001": Path(__file__).parent / "processed_ohdsi_sequences.h5"}


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


@app.route("/api/feature", methods=["GET"])
def get_feature():
    feature_idx = flask.request.args.get("label", default=None, type=int)

    filepath = _datasets["0001"]
    dataset = HDF5Dataset(filepath)

    if feature_idx is None:
        return {
            "status": STATUS_FAIL,
            "data": {"label": "missing required argument 'label'"},
        }

    try:
        x, y = dataset.feature(
            subset="processed", train_test="train", visit=10, feature=feature_idx
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
    except ValueError as err:
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
