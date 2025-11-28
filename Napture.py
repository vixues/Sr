"""
Data reader module for Neptune Plus™ ICP-MS .exp files.

This module provides the Napture class for reading and parsing
data files from Thermo Scientific Neptune Plus™ instruments.
"""

import pandas as pd
from typing import Optional, List
import os


class Napture:
    """
    Reader class for Neptune Plus™ ICP-MS .exp data files.
    
    This class handles parsing of the proprietary .exp file format
    and extracts measurement data into a pandas DataFrame.
    """
    
    def __init__(self):
        """Initialize the Napture reader."""
        self.filename: Optional[str] = None
        self.file: Optional[object] = None
    
    def open(self, filename: str, encoding: Optional[str] = None) -> None:
        """
        Open a data file for reading.
        
        Args:
            filename: Path to the .exp file
            encoding: File encoding (default: None, uses system default)
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")
        
        self.filename = filename
        self.file = open(self.filename, 'r', encoding=encoding)

    def getdata(self) -> pd.DataFrame:
        """
        Extract measurement data from the .exp file.
        
        Returns:
            DataFrame containing measurement data (columns 2-9, excluding Cycle and Time)
            
        Raises:
            ValueError: If the file format is invalid or data cannot be parsed
        """
        if self.filename is None:
            raise ValueError("No file opened. Call open() first.")
        
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"File not found: {self.filename}")
        
        try:
            # Find the header line containing 'Cycle'
            header_line = -1
            columns = None
            
            with open(self.filename, 'r', encoding='ascii') as f:
                for line_num, line in enumerate(f):
                    index = line.split()[:10]
                    if 'Cycle' in index:
                        header_line = line_num
                        columns = index
                        break
            
            if header_line == -1 or columns is None:
                raise ValueError("Could not find 'Cycle' header in file. Invalid file format.")
            
            # Read data rows
            data_rows: List[List[str]] = []
            
            with open(self.filename, 'r', encoding='ascii') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if i > header_line:
                        data = line.split()[:10]
                        # Stop at end marker
                        if '***' in data or not data:
                            break
                        # Skip empty lines
                        if len(data) >= 3:
                            data_rows.append(data)
            
            if not data_rows:
                raise ValueError("No data rows found in file.")
            
            # Create DataFrame using pd.concat (replacing deprecated append)
            dataframe = pd.DataFrame(data_rows, columns=columns)
            
            # Extract numeric columns (skip Cycle and Time, columns 0 and 1)
            numeric_data = dataframe.iloc[:, 2:].astype(float)
            
            return numeric_data
            
        except Exception as e:
            raise ValueError(f"Error parsing data file {self.filename}: {str(e)}")
