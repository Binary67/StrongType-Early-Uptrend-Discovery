import pandas as pd
import numpy as np
np.NaN = np.nan
import pandas_ta as ta


class DataLabel:
    def __init__(self, DataFrame):
        """
        Initialize DataLabel with a DataFrame containing OHLCV data.
        
        Args:
            DataFrame (pd.DataFrame): DataFrame with OHLCV data
        """
        self.DataFrame = DataFrame
    
    def LabelUptrend(self):
        """
        Label the data with prediction targets for upcoming EMA crossovers.
        
        Creates two labels:
        1. 'Uptrend': Current state where EMA 12 > EMA 50
        2. 'Label': 1 if EMA crossover will occur in next 3-10 days, 0 otherwise
        
        Returns:
            pd.DataFrame: DataFrame with added 'EMA12', 'EMA50', 'Uptrend', and 'Label' columns
        """
        # Calculate EMA 12 and EMA 50
        self.DataFrame['EMA12'] = ta.ema(self.DataFrame['Close'], length=12)
        self.DataFrame['EMA50'] = ta.ema(self.DataFrame['Close'], length=50)
        
        # Label current uptrend where EMA 12 > EMA 50
        self.DataFrame['Uptrend'] = (self.DataFrame['EMA12'] > self.DataFrame['EMA50']).astype(int)
        
        # Initialize prediction label and days until crossover
        self.DataFrame['Label'] = 0
        self.DataFrame['DaysUntilCrossover'] = 0
        
        # Look ahead 3-10 days to label upcoming crossovers
        for i in range(len(self.DataFrame) - 10):
            # Check if currently NOT in uptrend (EMA12 <= EMA50)
            if self.DataFrame['EMA12'].iloc[i] <= self.DataFrame['EMA50'].iloc[i]:
                # Check if crossover happens in next 3-10 days
                for j in range(3, 11):  # Days 3 through 10
                    if i + j < len(self.DataFrame):
                        # Check if crossover occurred
                        if (self.DataFrame['EMA12'].iloc[i+j] > self.DataFrame['EMA50'].iloc[i+j] and 
                            self.DataFrame['EMA12'].iloc[i+j-1] <= self.DataFrame['EMA50'].iloc[i+j-1]):
                            self.DataFrame.loc[self.DataFrame.index[i], 'Label'] = 1
                            self.DataFrame.loc[self.DataFrame.index[i], 'DaysUntilCrossover'] = j
                            break
        
        # Add debug information
        CrossoverCount = self.DataFrame['Label'].sum()
        print(f"   Total crossovers predicted in 3-10 day window: {CrossoverCount}")
        print(f"   Percentage of positive labels: {CrossoverCount/len(self.DataFrame)*100:.2f}%")
        
        return self.DataFrame
