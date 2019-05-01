# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np
import datetime
import math
from tkinter import ttk
import os
from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
from tkinter import messagebox
import sys
from calculation import Sr


class Mainwindow():
    
    def __init__(self,master):
        self.master = master
        self.master.resizable(0,0)
        sr_list = ('85Rb(v)','88Sr(v)','84Sr/86Sr','2σ','87Rb/86Sr','2σ','87Sr/86Sr','2σ','Time')
        pan_frame = Frame(self.master,width = 185.5,height = 600)
        pan_frame.grid(row = 0,column = 0, padx = 5,pady = 3,sticky=(N, S, E, W))
        pan_frame.grid_propagate(0)
        res_frame = Frame(self.master,width = 600, height = 600)
        res_frame.grid(row = 0,column = 1, padx = 5,pady = 3,sticky=(N, S, E, W))
        self.limit = StringVar()
        self.limit.set('1')
        self.k1 = StringVar()
        self.k1.set('0')
        self.s1 = StringVar()
        self.s1.set('70')
        self.k2 = StringVar()
        self.k2.set('40')
        self.s2 = StringVar()
        self.s2.set('200')
        self.sr_insert = StringVar()
        self.sr_insert.set('0.8853068815')
        self.filename = StringVar()
        self.re = pd.DataFrame()
        self.pathlabel = Label(pan_frame,text = 'Current Folder：',background = '#2F2F2F',foreground = 'White')
        self.pathlabel.pack(side = TOP, padx = 5,pady = 3,fill = X)
        Button(pan_frame,text = 'Choose Data Folder',command = lambda:self.choose_path(self.filename,self.pathlabel)).pack(side = TOP, padx = 5,pady = 3,fill = X)
        Label(pan_frame,text = 'Background Starts', background = '#2F2F2F',foreground = 'White').pack(side = TOP, padx = 5,pady = 3,fill = X)
        Entry(pan_frame,textvariable = self.k1).pack(side = TOP, padx = 5, pady = 3, fill = X)
        Label(pan_frame,text = 'Background Ends', background = '#2F2F2F',foreground = 'White').pack(side = TOP, padx = 5,pady = 3,fill = X)
        Entry(pan_frame,textvariable = self.k2).pack(side = TOP, padx = 5, pady = 3, fill = X)
        Label(pan_frame,text = 'Signal Starts', background = '#2F2F2F',foreground = 'White').pack(side = TOP, padx = 5,pady = 3,fill = X)
        Entry(pan_frame,textvariable = self.s1).pack(side = TOP, padx = 5, pady = 3, fill = X)
        Label(pan_frame,text = 'Signal Ends', background = '#2F2F2F',foreground = 'White').pack(side = TOP, padx = 5,pady = 3,fill = X)
        Entry(pan_frame,textvariable = self.s2).pack(side = TOP, padx = 5, pady = 3, fill = X)
        Label(pan_frame,text = '86.5 Valuation', background = '#2F2F2F',foreground = 'White').pack(side = TOP, padx = 5,pady = 3,fill = X)
        Entry(pan_frame,textvariable = self.sr_insert).pack(side = TOP,fill = X,padx = 5,pady = 3)

        Button(pan_frame,text = 'Run', command = self.calculation,background = '#B13254',foreground = 'White').pack(side = TOP, padx = 5,pady = 3,fill = X)
        self.text = Text(pan_frame, width = 30,height = 5,bd = 1)
        self.text.pack(side = TOP, padx = 5,pady = 3,fill = X)
        Button(pan_frame,text = 'Save Result',command  = self.savedata).pack(side = TOP, padx = 5,pady = 3,fill = X)
        Button(pan_frame,text = 'Exit', command  = self.exit).pack(side = BOTTOM, padx = 5,pady = 3,fill = X)

        bary = Scrollbar(res_frame)
        bary.pack(side = RIGHT,fill = Y)
        self.resultList = ttk.Treeview(res_frame, columns = sr_list, height = 30)
        self.resultList.column(column = '#0',width = 140)
        self.resultList.heading('#0', text="Sample")
        for i in range(len(sr_list)):
            self.resultList.heading(i, text = sr_list[i], anchor=E)
            self.resultList.column(i, minwidth=20, width= 80, anchor=E)
        self.resultList.column(2, width = 100)
        self.resultList.column(4, width = 100)
        self.resultList.column(6, width = 100)
        self.resultList.pack(side = TOP,fill = BOTH,expand = YES)
        bary.config(command = self.resultList.yview)
        self.resultList.config(yscrollcommand = bary.set)

    def choose_path(self,filename,label):
        fdir = askdirectory()
        filename.set(fdir)
        fn = fdir.split("/")
        label.config(text = "Current Folder:%s" % fn[-1])

    def calculation(self):
        now = datetime.datetime.now().strftime('%H:%M:%S')
        srdir = self.filename
        blanks = int(self.k1.get())
        signals = int(self.s1.get())
        blanke = int(self.k2.get())
        signale = int(self.s2.get())
        k = float(self.sr_insert.get())
        srfilelist = self.scan_file(srdir.get(), postfix = '.exp')
        self.text.insert(END,"%s:backgound%d～%d,signal%d~%d\n" % (now,blanks,blanke,signals,signale))
        i = 0
        report = pd.DataFrame()
        for items in srfilelist:
            filename = str(items)
            tmp = items.split('.')
            name = tmp[0]
            srfile = os.path.join(srdir.get(), filename)
            df = Sr(srfile)
            try:
                time = datetime.datetime.now().strftime('%H:%M:%S')
                df2 = df.cal(k, signals, signale, blanks, blanke)
                r = df.report(name)
                report = report.append(r, ignore_index = True)
                datatoshow = r.iloc[0].tolist()[1:]
                dataf = list(map(lambda x:'%2.7f' % x, datatoshow[0:-1]))
                dataf.append(time)
                self.resultList.insert('', i, text = name, values=tuple(dataf))
            except:
                time = datetime.datetime.now().strftime('%H:%M:%S')
                data = ['?????','?????','?????','?????','?????','?????','?????','?????',time]
                self.resultList.insert('', i,text = name, values=tuple(data))
            i += 1
        self.re = report
        spl = ('','','','','signal','%d～%d   ' % (signals,signale),'background:','%d～%d   ' % (blanks, blanke), now)
        self.resultList.insert('',0,text = '↘︎',values = spl,tags = 'head')
        self.resultList.tag_configure('head', background='#FF7349')
        report = pd.DataFrame()

    def savedata(self):
        savedir = askdirectory()
        reportname = os.path.join(savedir, 'report.xlsx')
        writer_o = pd.ExcelWriter(reportname)
        self.re.to_excel(writer_o)
        writer_o.save()

    def exit(self):
        self.master.destroy()

    def scan_file(self,directory,postfix = None):
        files_list = []
        for files in os.listdir(directory):
            if files.endswith(postfix):
                files_list.append(files)
        try:
            filelist.remove('.DS_Store')
        except:
            pass
        return files_list