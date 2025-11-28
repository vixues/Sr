# ICP-MS Strontium Isotope Data Processor

A professional Python application for processing ICP-MS Strontium isotope data from Thermo Scientific Neptune Plus™ High Resolution Multicollector ICP-MS instruments.

## Overview

This software provides a user-friendly graphical interface for:
- Reading and parsing `.exp` data files from Neptune Plus™ instruments
- Performing background correction and isotope ratio calculations
- Calculating 87Sr/86Sr, 84Sr/86Sr, and 87Rb/86Sr ratios with statistical analysis
- Exporting results to Excel format

## Features

- **Modern GUI**: Clean, intuitive interface with real-time status logging
- **Batch Processing**: Process multiple `.exp` files in a single operation
- **Background Correction**: Configurable background and signal regions
- **Statistical Analysis**: Automatic calculation of means, standard deviations, and 2σ errors
- **Data Export**: Save results to Excel format for further analysis
- **Error Handling**: Comprehensive error checking and user-friendly error messages

## Requirements

- **Python**: 3.7 or higher
- **Operating Systems**: Windows, Linux, macOS, BSD

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements-py3.txt
   ```

   Or install manually:
   ```bash
   pip install pandas>=1.3.0 numpy>=1.20.0 openpyxl>=3.0.0
   ```

## Usage

### Running the Application

```bash
python main.py
```

### Using the Interface

1. **Select Data Folder**: Click "Choose Data Folder" and select the directory containing your `.exp` files

2. **Configure Parameters**:
   - **Background Start/End**: Define the range of cycles for background measurement
   - **Signal Start/End**: Define the range of cycles for signal measurement
   - **86.5 Valuation**: Enter the correction factor (default: 0.8853068815)

3. **Run Calculation**: Click "Run Calculation" to process all `.exp` files in the selected folder

4. **View Results**: Results are displayed in the table with the following columns:
   - Sample name
   - 85Rb(v): Rubidium-85 voltage
   - 88Sr(v): Strontium-88 voltage
   - 84Sr/86Sr: Isotope ratio with 2σ error
   - 87Rb/86Sr: Rubidium/Strontium ratio with 2σ error
   - 87Sr/86Sr: Strontium isotope ratio with 2σ error
   - Time: Processing timestamp

5. **Save Results**: Click "Save Results" to export all results to an Excel file

## File Format

The application expects `.exp` files from Neptune Plus™ instruments with the following structure:
- Header line containing "Cycle"
- Data rows with columns: Cycle, Time, 83Kr, 83.5, 84Sr, 85Rb, 86Sr, 86.5, 87Sr, 88Sr
- End marker: `***`

## Project Structure

```
Sr/
├── main.py              # Application entry point
├── gui.py              # Graphical user interface
├── calculation.py      # Strontium isotope calculation engine
├── Napture.py          # Data file reader for .exp files
├── data/              # Sample data files
│   └── Sr-La.exp      # Example data file
├── requirements-py3.txt  # Python dependencies
└── README.md          # This file
```

## Technical Details

### Calculation Methods

The software performs the following calculations:

1. **Background Correction**: Subtracts mean background from signal region
2. **Mass Fractionation Correction**: Applies beta (β) correction factor
3. **Isotope Ratio Calculations**:
   - 84Sr/86Sr ratio with Kr interference correction
   - 87Rb/86Sr ratio with mass fractionation correction
   - 87Sr/86Sr ratio with Rb interference correction

### Statistical Output

For each ratio, the software calculates:
- **Mean**: Average value
- **SD**: Standard deviation
- **RSD**: Relative standard deviation
- **2SE**: 2× standard error
- **2RSE**: 2× relative standard error

## Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **openpyxl**: Excel file generation
- **tkinter**: GUI framework (included with Python)

## License

This software is released under the [MIT License](LICENSE).

## Notes

> **Note**: In the latest version of this software, the Sr and Hf programs are combined in the **Isotope** software. For more information, please visit [Isotope](http://www.geo-fo2.com).

## Troubleshooting

### Common Issues

1. **"No .exp files found"**: Ensure your data folder contains `.exp` files
2. **"Invalid input format"**: Check that all parameter fields contain valid numbers
3. **"File not found"**: Verify the selected folder path is correct
4. **Calculation errors**: Check that background and signal ranges are within the data range

### Error Messages

- Errors are displayed in the status log with timestamps
- Failed files are marked with "ERROR" in the results table
- Detailed error messages help identify the issue

## Contributing

Contributions are welcome! Please ensure code follows the existing style and includes appropriate documentation.

## Support

For issues, questions, or feature requests, please refer to the project repository.

---

**Enjoy processing your ICP-MS data!**
