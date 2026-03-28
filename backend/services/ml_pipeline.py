import pandas as pd
from pathlib import Path
import random
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

class DataManager:
    @staticmethod
    def load_csv(path_str: str, nrows=50000) -> pd.DataFrame:
        """
        Safely load datasets to avoid completely crashing if they aren't downloaded.
        """
        file_path = DATA_DIR / path_str
        if file_path.exists():
            return pd.read_csv(file_path, nrows=nrows)
        else:
            return DataManager.generate_fallback_data()

    @staticmethod
    def generate_fallback_data() -> pd.DataFrame:
        # 1000 rows of realistic mock tabular data matching typical net flow structures
        data = {
            "srcip": [f"192.168.1.{random.randint(1, 255)}" for _ in range(1000)],
            "dstip": [f"10.0.0.{random.randint(1, 255)}" for _ in range(1000)],
            "sport": np.random.randint(1024, 65535, 1000),
            "dsport": np.random.choice([80, 443, 22, 53, 3389], 1000),
            "proto": np.random.choice(["tcp", "udp"], 1000),
            "state": np.random.choice(["FIN", "INT", "CON", "REQ"], 1000),
            "dur": np.random.uniform(0.001, 10.0, 1000),
            "sbytes": np.random.randint(40, 5000, 1000),
            "dbytes": np.random.randint(40, 10000, 1000),
            "label": np.random.choice([0, 1], 1000, p=[0.9, 0.1])
        }
        return pd.DataFrame(data)

class XGBoostModel:
    def __init__(self):
        # Pending integration: Drop real weights here
        # import xgboost as xgb
        # self.model = xgb.Booster()
        # self.model.load_model('model.bst')
        self._is_loaded = True
        
    def predict(self, features: dict) -> dict:
        """
        Mock inference for an XGBoost Anomaly Detector on network traffic.
        """
        sbytes = features.get("sbytes", random.randint(100, 5000))
        dur = float(features.get("dur", random.uniform(0.1, 5.0)))
        
        anomaly_score = min(0.99, max(0.01, (sbytes / 5000) * 0.5 + (dur / 10) * 0.5))
        anomaly_score += random.uniform(-0.1, 0.1)
        anomaly_score = max(0.01, min(0.99, anomaly_score))
        
        is_anomaly = anomaly_score > 0.75
        
        return {
            "is_anomaly": is_anomaly,
            "confidence": round(anomaly_score, 3),
            "model": "XGBoost-UNSW-NB15"
        }

class GANSimulator:
    def __init__(self):
        # Pending integration: Drop real generator weights here
        # import torch
        # self.model = torch.load('gan_generator.pt')
        pass

    def generate_log(self, scenario: str) -> dict:
        """
        Mock inference representing a Generative Adversarial Network synthesizing log data.
        """
        base_log = {
            "source_ip": f"192.168.1.{random.randint(100,150)}",
            "event_type": "network_anomaly",
            "severity": "high",
            "raw_message": "Network traffic anomaly generated via GAN interpolation.",
            "metadata": {"source": "gan_synthesizer"}
        }
        
        if "credential" in scenario.lower():
            base_log["event_type"] = "authentication"
            base_log["raw_message"] = f"Failed login burst on core-banking internal dashboard. {random.randint(100,500)} attempts/sec."
        elif "sql" in scenario.lower():
            base_log["event_type"] = "transaction"
            base_log["raw_message"] = "SQL syntax anomaly detected in incoming request."
            
        return base_log

class SecureBERTClassifier:
    def __init__(self):
        # Pending integration:
        # from transformers import AutoTokenizer, AutoModelForSequenceClassification
        # self.tokenizer = AutoTokenizer.from_pretrained('ehsanaghaei/SecureBERT')
        # self.model = AutoModelForSequenceClassification.from_pretrained('ehsanaghaei/SecureBERT')
        pass

    def classify(self, text: str) -> dict:
        """
        Mock inference representing SecureBERT advanced NLP on massive log payloads.
        """
        return {
            "category": "malicious_payload",
            "tactics": ["T1059.001", "T1190"],
            "model": "SecureBERT-Mock",
            "score": round(random.uniform(0.8, 0.99), 3)
        }
