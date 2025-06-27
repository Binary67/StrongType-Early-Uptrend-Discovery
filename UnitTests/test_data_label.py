import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from DataLabel import DataLabel


def test_label_uptrend_adds_columns():
    Data = pd.DataFrame({"Close": list(range(60))})
    Labeler = DataLabel(Data)
    Labeled = Labeler.LabelUptrend()

    for Column in ["EMA12", "EMA50", "Uptrend", "Label", "DaysUntilCrossover"]:
        assert Column in Labeled.columns
