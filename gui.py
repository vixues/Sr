"""
Graphical User Interface for ICP-MS Strontium Data Processing.

This module provides a modern, user-friendly GUI for processing
Neptune Plus™ ICP-MS data files and calculating strontium isotope ratios.
"""

import pandas as pd
import numpy as np
import datetime
import os
import sys
from typing import Optional
from tkinter import ttk, messagebox, filedialog
from tkinter import Tk, Frame, Label, Entry, Button, Text, StringVar, X, Y, BOTH, TOP, BOTTOM, RIGHT, N, S, E, W, END
from calculation import Sr


class MainWindow:
    """
    Main application window for Sr isotope data processing.
    
    Provides a modern interface for:
    - Selecting data folders
    - Configuring calculation parameters
    - Running calculations
    - Viewing and exporting results
    """
    
    # Color scheme
    BG_COLOR = '#2C3E50'
    PANEL_BG = '#34495E'
    ACCENT_COLOR = '#3498DB'
    SUCCESS_COLOR = '#27AE60'
    ERROR_COLOR = '#E74C3C'
    TEXT_COLOR = '#ECF0F1'
    BUTTON_HOVER = '#2980B9'
    
    def __init__(self, master: Tk):
        """
        Initialize the main window.
        
        Args:
            master: Tkinter root window
        """
        self.master = master
        self.master.title("ICP-MS Strontium Isotope Data Processor")
        self.master.configure(bg=self.BG_COLOR)
        self.master.resizable(True, True)
        self.master.minsize(900, 650)
        
        # Configure style
        self._setup_styles()
        
        # Data storage
        self.filename = StringVar()
        self.re = pd.DataFrame()
        
        # Parameter variables
        self.k1 = StringVar(value='0')
        self.k2 = StringVar(value='40')
        self.s1 = StringVar(value='70')
        self.s2 = StringVar(value='200')
        self.sr_insert = StringVar(value='0.8853068815')
        
        # Build UI
        self._create_widgets()
        
    def _setup_styles(self):
        """Configure ttk styles for modern appearance."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Action.TButton',
                       padding=10,
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Primary.TButton',
                       padding=8,
                       font=('Segoe UI', 9))
        
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container
        main_container = Frame(self.master, bg=self.BG_COLOR)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls
        pan_frame = Frame(main_container, bg=self.PANEL_BG, relief='flat', bd=2)
        pan_frame.pack(side='left', fill=Y, padx=(0, 10))
        pan_frame.config(width=250)
        
        # Right panel for results
        res_frame = Frame(main_container, bg=self.BG_COLOR)
        res_frame.pack(side='right', fill=BOTH, expand=True)
        
        # Left panel widgets
        self._create_control_panel(pan_frame)
        
        # Right panel widgets
        self._create_results_panel(res_frame)
        
    def _create_control_panel(self, parent: Frame):
        """Create the control panel with input fields and buttons."""
        # Title
        title = Label(parent, text="Sr Isotope Processor", 
                     bg=self.PANEL_BG, fg=self.TEXT_COLOR,
                     font=('Segoe UI', 14, 'bold'))
        title.pack(side=TOP, pady=(15, 20), padx=10)
        
        # File selection
        file_frame = Frame(parent, bg=self.PANEL_BG)
        file_frame.pack(side=TOP, fill=X, padx=10, pady=5)
        
        self.pathlabel = Label(file_frame, text='No folder selected', 
                              bg=self.PANEL_BG, fg=self.TEXT_COLOR,
                              font=('Segoe UI', 9),
                              wraplength=220, justify='left')
        self.pathlabel.pack(side=TOP, pady=(0, 5))
        
        btn_choose = Button(file_frame, text='📁 Choose Data Folder', 
                           command=self._choose_path,
                           bg=self.ACCENT_COLOR, fg='white',
                           font=('Segoe UI', 9, 'bold'),
                           relief='flat', padx=10, pady=8,
                           cursor='hand2')
        btn_choose.pack(side=TOP, fill=X)
        
        # Separator
        separator = Frame(parent, bg='#7F8C8D', height=1)
        separator.pack(side=TOP, fill=X, padx=10, pady=15)
        
        # Parameters section
        params_label = Label(parent, text="Calculation Parameters", 
                           bg=self.PANEL_BG, fg=self.TEXT_COLOR,
                           font=('Segoe UI', 10, 'bold'))
        params_label.pack(side=TOP, pady=(0, 10), padx=10)
        
        # Background range
        self._create_param_entry(parent, 'Background Start:', self.k1)
        self._create_param_entry(parent, 'Background End:', self.k2)
        
        # Signal range
        self._create_param_entry(parent, 'Signal Start:', self.s1)
        self._create_param_entry(parent, 'Signal End:', self.s2)
        
        # 86.5 Valuation
        self._create_param_entry(parent, '86.5 Valuation:', self.sr_insert)
        
        # Separator
        separator2 = Frame(parent, bg='#7F8C8D', height=1)
        separator2.pack(side=TOP, fill=X, padx=10, pady=15)
        
        # Action buttons
        btn_run = Button(parent, text='▶ Run Calculation', 
                        command=self._calculation,
                        bg=self.SUCCESS_COLOR, fg='white',
                        font=('Segoe UI', 10, 'bold'),
                        relief='flat', padx=10, pady=12,
                        cursor='hand2')
        btn_run.pack(side=TOP, fill=X, padx=10, pady=5)
        
        # Status text
        status_label = Label(parent, text="Status Log:", 
                           bg=self.PANEL_BG, fg=self.TEXT_COLOR,
                           font=('Segoe UI', 9, 'bold'))
        status_label.pack(side=TOP, pady=(15, 5), padx=10, anchor='w')
        
        self.text = Text(parent, width=30, height=6, bd=1, 
                        bg='#1C1C1C', fg='#00FF00',
                        font=('Consolas', 8),
                        relief='flat', wrap='word')
        self.text.pack(side=TOP, fill=X, padx=10, pady=(0, 10))
        
        # Save button
        btn_save = Button(parent, text='💾 Save Results', 
                         command=self._savedata,
                         bg=self.ACCENT_COLOR, fg='white',
                         font=('Segoe UI', 9),
                         relief='flat', padx=10, pady=8,
                         cursor='hand2')
        btn_save.pack(side=TOP, fill=X, padx=10, pady=5)
        
        # Exit button
        btn_exit = Button(parent, text='✖ Exit', 
                         command=self._exit,
                         bg='#95A5A6', fg='white',
                         font=('Segoe UI', 9),
                         relief='flat', padx=10, pady=8,
                         cursor='hand2')
        btn_exit.pack(side=BOTTOM, fill=X, padx=10, pady=(10, 15))
        
    def _create_param_entry(self, parent: Frame, label_text: str, var: StringVar):
        """Create a labeled entry field for parameters."""
        frame = Frame(parent, bg=self.PANEL_BG)
        frame.pack(side=TOP, fill=X, padx=10, pady=3)
        
        label = Label(frame, text=label_text, 
                     bg=self.PANEL_BG, fg=self.TEXT_COLOR,
                     font=('Segoe UI', 9),
                     width=15, anchor='w')
        label.pack(side='left', padx=(0, 5))
        
        entry = Entry(frame, textvariable=var, 
                     bg='white', fg='black',
                     font=('Segoe UI', 9),
                     relief='flat', bd=1)
        entry.pack(side='right', fill=X, expand=True)
        
    def _create_results_panel(self, parent: Frame):
        """Create the results display panel."""
        # Title
        title = Label(parent, text="Results", 
                     bg=self.BG_COLOR, fg=self.TEXT_COLOR,
                     font=('Segoe UI', 14, 'bold'))
        title.pack(side=TOP, pady=(0, 10), anchor='w')
        
        # Results table
        sr_list = ('85Rb(v)', '88Sr(v)', '84Sr/86Sr', '2σ', 
                  '87Rb/86Sr', '2σ', '87Sr/86Sr', '2σ', 'Time')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Treeview
        self.resultList = ttk.Treeview(parent, columns=sr_list, height=25,
                                       yscrollcommand=scrollbar.set,
                                       show='tree headings')
        scrollbar.config(command=self.resultList.yview)
        
        # Configure columns
        self.resultList.column('#0', width=150, anchor='w')
        self.resultList.heading('#0', text="Sample")
        
        for i, col in enumerate(sr_list):
            self.resultList.heading(i, text=col, anchor=E)
            width = 100 if i in [2, 4, 6] else 80
            self.resultList.column(i, minwidth=60, width=width, anchor=E)
        
        self.resultList.pack(side=TOP, fill=BOTH, expand=True)
        
        # Configure tag for header row
        self.resultList.tag_configure('header', background='#3498DB', 
                                     foreground='white', font=('Segoe UI', 9, 'bold'))
        self.resultList.tag_configure('error', background='#E8E8E8', 
                                     foreground='#E74C3C')
        
    def _choose_path(self):
        """Open directory dialog to select data folder."""
        fdir = filedialog.askdirectory(title="Select Data Folder")
        if fdir:
            self.filename.set(fdir)
            folder_name = os.path.basename(fdir)
            self.pathlabel.config(text=f"📂 {folder_name}")
            self._log_status(f"Selected folder: {folder_name}")
    
    def _validate_inputs(self) -> tuple:
        """
        Validate user inputs.
        
        Returns:
            Tuple of (is_valid, error_message, params_dict)
        """
        try:
            blanks = int(self.k1.get())
            blanke = int(self.k2.get())
            signals = int(self.s1.get())
            signale = int(self.s2.get())
            k = float(self.sr_insert.get())
            
            if blanks < 0 or blanke < 0 or signals < 0 or signale < 0:
                return False, "All indices must be non-negative integers.", None
            
            if blanks >= blanke:
                return False, "Background start must be less than background end.", None
            
            if signals >= signale:
                return False, "Signal start must be less than signal end.", None
            
            if not self.filename.get():
                return False, "Please select a data folder first.", None
            
            if not os.path.exists(self.filename.get()):
                return False, "Selected folder does not exist.", None
            
            params = {
                'blanks': blanks,
                'blanke': blanke,
                'signals': signals,
                'signale': signale,
                'k': k
            }
            
            return True, "", params
            
        except ValueError as e:
            return False, f"Invalid input format: {str(e)}", None
    
    def _calculation(self):
        """Perform calculations on all .exp files in the selected folder."""
        # Validate inputs
        is_valid, error_msg, params = self._validate_inputs()
        if not is_valid:
            messagebox.showerror("Input Error", error_msg)
            return
        
        # Get file list
        srfilelist = self._scan_file(self.filename.get(), postfix='.exp')
        if not srfilelist:
            messagebox.showwarning("No Files", 
                                  "No .exp files found in the selected folder.")
            return
        
        # Clear previous results
        for item in self.resultList.get_children():
            self.resultList.delete(item)
        
        # Log start
        now = datetime.datetime.now().strftime('%H:%M:%S')
        self._log_status(f"{now}: Starting calculation...")
        self._log_status(f"Background: {params['blanks']}-{params['blanke']}, "
                        f"Signal: {params['signals']}-{params['signale']}")
        self._log_status(f"Found {len(srfilelist)} file(s)")
        
        # Process files
        report_list = []
        successful = 0
        failed = 0
        
        for i, filename in enumerate(srfilelist):
            try:
                # Extract sample name
                name = os.path.splitext(filename)[0]
                srfile = os.path.join(self.filename.get(), filename)
                
                # Process file
                df = Sr(srfile)
                df.cal(params['k'], params['signals'], params['signale'], 
                      params['blanks'], params['blanke'])
                r = df.report(name)
                report_list.append(r)
                
                # Display results
                time = datetime.datetime.now().strftime('%H:%M:%S')
                datatoshow = r.iloc[0].tolist()[1:]
                dataf = [f'{x:.7f}' if isinstance(x, (int, float)) else str(x) 
                        for x in datatoshow[:-1]]
                dataf.append(time)
                
                self.resultList.insert('', END, text=name, values=tuple(dataf))
                successful += 1
                
            except Exception as e:
                # Log error
                time = datetime.datetime.now().strftime('%H:%M:%S')
                error_data = ['ERROR'] * 8 + [time]
                self.resultList.insert('', END, text=name, 
                                     values=tuple(error_data), tags='error')
                self._log_status(f"Error processing {name}: {str(e)}")
                failed += 1
        
        # Combine reports
        if report_list:
            self.re = pd.concat(report_list, ignore_index=True)
        else:
            self.re = pd.DataFrame()
        
        # Add header row
        header_values = ('', '', '', '', 'Signal', 
                        f"{params['signals']}-{params['signale']}", 
                        'Background:', 
                        f"{params['blanks']}-{params['blanke']}", now)
        self.resultList.insert('', 0, text='↘ Parameters', 
                              values=header_values, tags='header')
        
        # Summary
        self._log_status(f"Completed: {successful} successful, {failed} failed")
        
        if successful > 0:
            messagebox.showinfo("Calculation Complete", 
                              f"Successfully processed {successful} file(s).\n"
                              f"Failed: {failed} file(s).")
    
    def _savedata(self):
        """Save results to Excel file."""
        if self.re.empty:
            messagebox.showwarning("No Data", 
                                 "No results to save. Please run calculation first.")
            return
        
        try:
            savedir = filedialog.askdirectory(title="Select Save Location")
            if savedir:
                reportname = os.path.join(savedir, 'report.xlsx')
                
                with pd.ExcelWriter(reportname, engine='openpyxl') as writer:
                    self.re.to_excel(writer, index=False, sheet_name='Results')
                
                self._log_status(f"Results saved to: {reportname}")
                messagebox.showinfo("Save Successful", 
                                  f"Results saved to:\n{reportname}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")
            self._log_status(f"Save error: {str(e)}")
    
    def _exit(self):
        """Exit the application."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.master.destroy()
    
    def _scan_file(self, directory: str, postfix: Optional[str] = None) -> list:
        """
        Scan directory for files with specified extension.
        
        Args:
            directory: Directory to scan
            postfix: File extension to filter (e.g., '.exp')
            
        Returns:
            List of matching filenames
        """
        if not os.path.isdir(directory):
            return []
        
        files_list = []
        try:
            for file in os.listdir(directory):
                if postfix and file.endswith(postfix):
                    # Skip system files
                    if file != '.DS_Store':
                        files_list.append(file)
        except PermissionError:
            self._log_status(f"Permission denied: {directory}")
        
        return sorted(files_list)
    
    def _log_status(self, message: str):
        """
        Add a message to the status log.
        
        Args:
            message: Message to log
        """
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.text.insert(END, f"[{timestamp}] {message}\n")
        self.text.see(END)