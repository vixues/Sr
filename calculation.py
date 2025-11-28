"""
Strontium isotope calculation module for ICP-MS data processing.

This module provides the Sr class for processing and calculating
strontium isotope ratios from Neptune Plus™ ICP-MS data files.
"""

import pandas as pd
import numpy as np
import math
from typing import Optional, Union
from Napture import Napture


class Sr:
    """
    Strontium isotope calculation class for ICP-MS data processing.
    
    This class handles data loading, background correction, and calculation
    of strontium isotope ratios including 87Sr/86Sr, 84Sr/86Sr, and 87Rb/86Sr.
    """
    
    # Physical constants for isotope calculations
    ISOTOPE_RATIO_88_86 = 8.375209  # Natural ratio
    MASS_87_86_LOG = math.log(87.905619 / 85.909267)
    MASS_83_86_RATIO = 83.91343 / 85.909267
    MASS_83_88_RATIO = 83.91343 / 87.905619
    MASS_86_87_RATIO = 86.909187 / 85.909267
    MASS_84_87_RATIO = 84.911794 / 86.909187
    MASS_86_87_SR_RATIO = 86.908884 / 85.909267
    
    # Correction factors
    KR_83_5_RATIO = 33.6 / 22.95
    KR_83_84_RATIO = 57 / 11.5
    KR_83_86_RATIO = 17.3 / 11.5
    KR_83_5_84_RATIO = 26.8 / 22.95
    RB_85_87_RATIO = 27.835 / 72.165

    def __init__(self, file: str):
        """
        Initialize Sr calculation object.
        
        Args:
            file: Path to the .exp data file from Neptune Plus™ ICP-MS
        """
        self.filename = file
        self.df: Optional[pd.DataFrame] = None
        self.name: Optional[str] = None
        
        try:
            machine_type = Napture()
            machine_type.open(self.filename, encoding='ascii')
            self.df = machine_type.getdata()
        except Exception as e:
            raise ValueError(f"Failed to load data file {file}: {str(e)}")
    
    def negative_filter(self, x: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        Filter out negative values by converting them to NaN.
        
        Args:
            x: Value or Series to filter
            
        Returns:
            Filtered value or Series with negative values set to NaN
        """
        if isinstance(x, pd.Series):
            return x.where(x >= 0, np.nan)
        return np.nan if x < 0 else x

    def std_filter(self, x: pd.Series, std_scaler: float = 1.0) -> pd.Series:
        """
        Filter outliers based on standard deviation.
        
        Args:
            x: Series to filter
            std_scaler: Multiplier for standard deviation threshold
            
        Returns:
            Filtered Series with outliers set to NaN
        """
        mean = x.mean()
        std = x.std()
        threshold = std_scaler * std
        
        def filter_func(val: float) -> float:
            if pd.isna(val) or abs(val - mean) > threshold:
                return np.nan
            return val
        
        return x.apply(filter_func)

    def cal(self, k: float, signals: int, signale: int, 
            blanks: int, blanke: int) -> pd.DataFrame:
        """
        Perform strontium isotope calculations with background correction.
        
        Args:
            k: 86.5 valuation factor
            signals: Start index for signal region
            signale: End index for signal region
            blanks: Start index for background region
            blanke: End index for background region
            
        Returns:
            DataFrame with calculated isotope ratios and statistics
        """
        if self.df is None:
            raise ValueError("Data not loaded. Initialize with valid file.")
        
        # Background correction
        background_mean = self.df[blanks:blanke].mean()
        self.df = self.df[signals:signale] - background_mean
        
        # Set column names
        self.df.columns = ['83Kr', '83.5', '84Sr', '85Rb', '86Sr', '86.5', '87Sr', '88Sr']
        
        # Insert calculated 85.4 column
        self.df.insert(3, '85.4', self.df['86.5'] * k)
        
        # Calculate beta factor (mass fractionation correction)
        kr_correction = (self.df['83Kr'] - self.df['83.5'] * self.KR_83_5_RATIO) * self.KR_83_86_RATIO
        corrected_86 = self.df['86Sr'] - kr_correction
        
        beta_8_6 = (
            math.log(1 / 0.1194) - 
            self.df['88Sr'].apply(math.log) + 
            corrected_86.apply(math.log)
        ) / self.MASS_87_86_LOG
        
        self.df['𝛽8/6'] = beta_8_6
        
        # Calculate 84Sr/86Sr ratio
        kr_84_correction = (
            self.df['83.5'] * self.KR_83_5_84_RATIO + 
            (self.df['83Kr'] - self.df['83.5'] * self.KR_83_5_RATIO) * self.KR_83_84_RATIO
        )
        corrected_84 = self.df['84Sr'] - kr_84_correction
        
        self.df['4/6Sr'] = (
            corrected_84 / corrected_86 * 
            beta_8_6.apply(lambda x: math.pow(self.MASS_83_86_RATIO, x))
        )
        
        # Calculate 84Sr/88Sr ratio
        self.df['4/8Sr'] = (
            corrected_84 / self.df['88Sr'] * 
            beta_8_6.apply(lambda x: math.pow(self.MASS_83_88_RATIO, x))
        )
        
        # Calculate 87Rb/86Sr ratio
        self.df['7Rb/6Sr'] = (
            (self.df['85Rb'] * self.RB_85_87_RATIO) / corrected_86 * 
            beta_8_6.apply(lambda x: math.pow(self.MASS_86_87_RATIO, x))
        )
        
        # Calculate 87Sr/86Sr ratio
        rb_correction = (
            self.df['85Rb'] * self.RB_85_87_RATIO * 
            beta_8_6.apply(lambda x: math.pow(self.MASS_84_87_RATIO, x))
        )
        corrected_87 = self.df['87Sr'] - rb_correction
        
        self.df['7/6Sr'] = (
            corrected_87 / corrected_86 * 
            beta_8_6.apply(lambda x: math.pow(self.MASS_86_87_SR_RATIO, x))
        )
        
        # Calculate statistics
        mean = self.df.mean()
        sd = self.df.std()
        rsd = sd / mean
        count = self.df.count().astype(float)
        count_sqrt = count.apply(math.sqrt)
        se = 2 * sd / count_sqrt
        rse = se / mean
        
        # Append statistics using pd.concat (replacing deprecated append)
        stats_data = {
            'Mean': mean,
            'SD': sd,
            'RSD': rsd,
            '2SE': se,
            '2RSE': rse
        }
        
        stats_df = pd.DataFrame(stats_data).T
        self.df = pd.concat([self.df, stats_df], ignore_index=False)
        
        return self.df

    def report(self, name: str) -> pd.DataFrame:
        """
        Generate a summary report for the sample.
        
        Args:
            name: Sample name
            
        Returns:
            DataFrame with summary statistics
        """
        if self.df is None:
            raise ValueError("No calculation data available. Run cal() first.")
        
        self.name = str(name)
        
        try:
            final = {
                'Sample': self.name,
                '85Rb(v)': self.df.loc['Mean', '85Rb'],
                '88Sr(v)': self.df.loc['Mean', '88Sr'],
                '84Sr/86Sr': self.df.loc['Mean', '4/6Sr'],
                '2σ': self.df.loc['2SE', '4/6Sr'],
                '87Rb/86Sr': self.df.loc['Mean', '7Rb/6Sr'],
                '2σ1': self.df.loc['2SE', '7Rb/6Sr'],
                '87Sr/86Sr': self.df.loc['Mean', '7/6Sr'],
                '2σ2': self.df.loc['2SE', '7/6Sr']
            }
        except KeyError as e:
            raise ValueError(f"Missing required data in calculation results: {str(e)}")
        
        result = pd.DataFrame(
            data=[final],
            columns=['Sample', '85Rb(v)', '88Sr(v)', '84Sr/86Sr', '2σ', 
                    '87Rb/86Sr', '2σ1', '87Sr/86Sr', '2σ2']
        )
        return result