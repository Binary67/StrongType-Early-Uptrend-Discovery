import logging
import pandas as pd
from Indicator import Indicator


class DataLabel:
    """Add labeling for uptrend discovery."""

    def __init__(self, IndicatorLib: Indicator | None = None) -> None:
        self.IndicatorLib = IndicatorLib if IndicatorLib else Indicator()
        self.Logger = logging.getLogger(self.__class__.__name__)

    def AddLabel(self, Data: pd.DataFrame) -> pd.DataFrame:
        """Generate ``Uptrend`` and ``Label`` columns.

        ``Uptrend`` is ``1`` when ``EMA 12`` is greater than ``EMA 50``.
        ``Label`` is ``1`` if any of the next ten days contain an ``Uptrend``.
        """

        self.Logger.info("Calculating EMA 12 and EMA 50 for labeling")
        Ema12 = self.IndicatorLib.EMA(Data["Close"], 12)
        Ema50 = self.IndicatorLib.EMA(Data["Close"], 50)

        Data["Uptrend"] = (Ema12 > Ema50).astype(int)

        self.Logger.info("Computing future uptrend-based labels")
        FutureShifts = [Data["Uptrend"].shift(-i) for i in range(1, 11)]
        FutureMatrix = pd.concat(FutureShifts, axis=1)
        Data["Label"] = FutureMatrix.max(axis=1).fillna(0).astype(int)

        Positive = int(Data["Label"].sum())
        Total = len(Data)
        self.Logger.info(
            "Generated labels with %d positives out of %d entries", Positive, Total
        )
        return Data
