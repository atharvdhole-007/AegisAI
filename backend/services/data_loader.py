import pandas as pd
from pathlib import Path
from services.ml_pipeline import DataManager

class DataLoaderService:
    @staticmethod
    def load_unsw_nb15():
        return DataManager.load_csv("core/unsw_nb15/UNSW_NB15_training-set.csv")

    @staticmethod
    def load_creditcard_fraud():
        return DataManager.load_csv("core/creditcard_fraud/creditcard.csv")

data_loader = DataLoaderService()
