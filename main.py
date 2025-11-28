"""
Main entry point for ICP-MS Strontium Isotope Data Processor.

This application provides a graphical interface for processing
Neptune Plus™ ICP-MS data files and calculating strontium isotope ratios.
"""

from tkinter import Tk
from gui import MainWindow


def main():
    """Initialize and run the main application."""
    root = Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()