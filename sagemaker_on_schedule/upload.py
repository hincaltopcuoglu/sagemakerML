import json
import os
from io import StringIO

import joblib
import numpy as np
from numpy import atleast_2d, loadtxt


def model_fn(model_dir):
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf


def input_fn(input_data: str, content_type):
    if content_type != "text/csv":
        raise ValueError("Must pass utf-8 encoded CSV as input")
    data_in = loadtxt(StringIO(input_data), delimiter=",")
    return atleast_2d(data_in)


def output_fn(prediction, content_type):
    if content_type == "application/json":
        res = prediction.tolist()
        respJSON = {"Output": res}
        return json.dumps(respJSON)
    elif content_type == "text/csv":
        s = StringIO()
        np.savetxt(s, prediction, fmt="%d", delimiter=",", newline="\n")
        return s.getvalue()
    else:
        raise ValueError("This model only supports text/csv or application/json input")
