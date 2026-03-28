import os
import sys
import subprocess
from pathlib import Path

# Provide helpful feedback if dependencies are missing, per user specs
try:
    import requests
except ImportError:
    print("Error: The 'requests' library is not installed.")
    print("Please run: pip install requests")
    sys.exit(1)

try:
    import builtins
    # We don't strictly require kaggle module import at top-level 
    # since we use the CLI, but we'll try to check if CLI is available later.
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

DATASETS = [
    {
        "name": "UNSW-NB15 Training",
        "url": "https://cloudstor.aarnet.edu.au/plus/s/2DhnLGDtc87sVUY/download?path=%2FReal%20Capture%20Training%2F&files=UNSW_NB15_training-set.csv",
        "path": DATA_DIR / "core" / "unsw_nb15" / "UNSW_NB15_training-set.csv",
        "method": "download"
    },
    {
        "name": "UNSW-NB15 Testing",
        "url": "https://cloudstor.aarnet.edu.au/plus/s/2DhnLGDtc87sVUY/download?path=%2FReal%20Capture%20Testing%2F&files=UNSW_NB15_testing-set.csv",
        "path": DATA_DIR / "core" / "unsw_nb15" / "UNSW_NB15_testing-set.csv",
        "method": "download"
    },
    {
        "name": "Credit Card Fraud (Kaggle)",
        "dataset": "mlg-ulb/creditcardfraud",
        "path": DATA_DIR / "core" / "creditcard_fraud" / "creditcard.csv",
        "out_dir": DATA_DIR / "core" / "creditcard_fraud",
        "method": "kaggle"
    },
    {
        "name": "MITRE ATT&CK Enterprise JSON",
        "url": "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json",
        "path": DATA_DIR / "core" / "mitre_attck_banking" / "enterprise-attack.json",
        "method": "download"
    },
    {
        "name": "Blocklist.de IP blocklist",
        "url": "https://lists.blocklist.de/lists/all.txt",
        "path": DATA_DIR / "threat_intel" / "blocklist_de" / "blocklist_ips.txt",
        "method": "download"
    }
]

def download_file(url, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def download_kaggle(dataset, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Try using Kaggle CLI via subprocess
    try:
        result = subprocess.run(
            [sys.executable, "-m", "kaggle", "datasets", "download", "-d", dataset, "-p", str(out_dir), "--unzip"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            # Fallback to direct command if module execution failed
            result2 = subprocess.run(
                ["kaggle", "datasets", "download", "-d", dataset, "-p", str(out_dir), "--unzip"],
                capture_output=True, text=True
            )
            if result2.returncode != 0:
                raise Exception(f"Kaggle CLI failed. Ensure 'kaggle' is installed, and KAGGLE_USERNAME / KAGGLE_KEY are correctly set.\nDetails: {result2.stderr.strip()}")
            
    except FileNotFoundError:
        raise Exception("Kaggle command not found. Please 'pip install kaggle' and set your credentials.")


def main():
    print("=" * 50)
    print("AegisAI - Automated Dataset Setup")
    print("=" * 50)
    print(f"Target Directory: {DATA_DIR}\n")

    summary = []

    for ds in DATASETS:
        print(f"Downloading {ds['name']}...")
        if ds['path'].exists():
            print(f"  -> File exactly exists, skipping.")
            summary.append(f"Skipped (Exists): {ds['name']}")
            continue
        
        try:
            if ds['method'] == 'download':
                download_file(ds['url'], ds['path'])
                summary.append(f"Success: {ds['name']}")
                print(f"  -> Done.")
            elif ds['method'] == 'kaggle':
                download_kaggle(ds['dataset'], ds['out_dir'])
                summary.append(f"Success: {ds['name']}")
                print(f"  -> Done.")
        except Exception as e:
            print(f"  -> Failed: {e}")
            summary.append(f"Failed: {ds['name']} -> {e}")

    print("\n" + "=" * 50)
    print("Download Summary")
    print("=" * 50)
    for s in summary:
        print(f" - {s}")

if __name__ == "__main__":
    main()
