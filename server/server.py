"""
Flask application to serve data in JSON API. Only GET requests are implemented.

TODO: extend this slowly into an hdf5 server. The days here are like labels, and the
    todo items are features.
"""

import math
import random

import flask
import flask_cors

# JSend spec https://github.com/omniti-labs/jsend
STATUS_SUCCESS = "success"
STATUS_FAIL = "fail"
STATUS_ERROR = "error"

app = flask.Flask(__name__)
flask_cors.CORS(app)  # TODO: remove for production. Enable CORS during development.

_labels = ["Hematocrit", "Serum [Na+]", "Serum pH", "Urobilin"]
_features = [
    [math.sin(x * random.random()) + 2.0 for x in range(10)],
    [math.cos(x * random.random()) + 0.5 for x in range(10)],
    [math.tan(x * random.random()) - 1.0 for x in range(10)],
    [math.sin(x * random.random()) + 2.5 for x in range(10)],
]


@app.route("/api/labels", methods=["GET"])
def get_labels():
    return {
        "status": STATUS_SUCCESS,
        "data": {"labels": [{"value": j, "name": label} for j, label in enumerate(_labels)]},
    }


@app.route("/api/features", methods=["GET"])
def get_todos():
    return {
        "status": STATUS_SUCCESS,
        "data": {"features": _features},
    }


@app.route("/api/feature", methods=["GET"])
def get_todo():
    label_idx = flask.request.args.get("label", default=None, type=int)

    if label_idx is None:
        return {
            "status": STATUS_FAIL,
            "data": {"label": f"missing required argument 'label'"},
        }

    if label_idx >= 0 and label_idx <= len(_labels):
        feature = _features[label_idx]
        return {
            "status": STATUS_SUCCESS,
            "data": {
                "feature": [{"x": i, "y": j} for (i, j) in enumerate(feature)],
                "label": {"value": label_idx, "name": _labels[label_idx]},
            }}

    return {
        "status": STATUS_FAIL,
        "data": {"label": f"'label' must be an integer in [0, {len(_labels)}] but got {label_idx}"},
    }
