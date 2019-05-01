# -*- coding: UTF-8 -*-
import pandas as pd
from Napture import Napture
import math


class Sr():

    def __init__(self, file):
        self.filename = file
        machine_type = Napture()
        machine_type.open(self.filename, encoding='ascii')
        self.df = machine_type.getdata()
    
    def negtive_fil(self, x):
        if x < 0:
            x = np.Nan
        return x

    def std_filter(self, x, std_scaler=1):
        mean = x.mean()
        std = x.std()
        def fil(x):
            if abs(x - mean) > std_scaler * std:
                x = np.NaN
            return x
        x = x.apply(fil)
        return x

    def cal(self, k, signals, signale, blanks, blanke):
        self.df = (self.df[signals:signale] - self.df[blanks:blanke].mean())
        #print(self.df)
        self.df.columns = ['83Kr','83.5','84Sr','85Rb','86Sr','86.5','87Sr','88Sr']
        self.df.insert(3, '85.4', self.df['86.5'] * k)
        self.df['𝛽8/6']= (math.log(1/0.1194) - self.df['88Sr'].apply(math.log) + (self.df['86Sr']-((self.df['83Kr']-self.df['83.5']*33.6/22.95)*17.3/11.5)).apply(math.log))/math.log(87.905619/85.909267)
        self.df['4/6Sr'] = (self.df['84Sr'] - self.df['83.5']*26.8/22.95-((self.df['83Kr']-self.df['83.5']*33.6/22.95)*57/11.5))/(self.df['86Sr']-((self.df['83Kr']-self.df['83.5']*33.6/22.95)*17.3/11.5))*self.df['𝛽8/6'].apply(lambda x:math.pow(83.91343/85.909267,x))
        self.df['4/8Sr'] = (self.df['84Sr'] - self.df['83.5']*26.8/22.95-((self.df['83Kr']-self.df['83.5']*33.6/22.95)*57/11.5))/self.df['88Sr']*self.df['𝛽8/6'].apply(lambda x:math.pow(83.91343/87.905619,x))
        self.df['7Rb/6Sr'] = (self.df['85Rb'] * 27.835 / 72.165) / self.df['86Sr']*self.df['𝛽8/6'].apply(lambda x:math.pow(86.909187/85.909267,x))
        self.df['7/6Sr'] = (self.df['87Sr']-self.df['85Rb']*27.835/72.165*self.df['𝛽8/6'].apply(lambda x:math.pow(84.911794/86.909187,x)))/self.df['86Sr']*self.df['𝛽8/6'].apply(lambda x:math.pow(86.908884/85.909267,x))
        mean = self.df.mean()
        sd = self.df.std()
        rsd = sd / mean
        count = self.df.count()
        count.astype(float)
        count_sqrt = count.apply(math.sqrt)
        se = 2 * sd / count_sqrt
        rse = se / mean
        self.df = self.df.append(pd.DataFrame(data = mean).rename(columns = {0:'Mean'}).T)
        self.df = self.df.append(pd.DataFrame(data = sd).rename(columns = {0:'SD'}).T)
        self.df = self.df.append(pd.DataFrame(data = rsd).rename(columns = {0:'RSD'}).T)
        self.df = self.df.append(pd.DataFrame(data = se).rename(columns = {0:'2SE'}).T)
        self.df = self.df.append(pd.DataFrame(data = rse).rename(columns = {0:'2RSE'}).T)
        return self.df

    def report(self, name):
        self.name = str(name)
        final = {
        'Sample':self.name,
        '85Rb(v)':self.df.loc['Mean','85Rb'],
        '88Sr(v)':self.df.loc['Mean','88Sr'],
        '84Sr/86Sr':self.df.loc['Mean','4/6Sr'],
        '2σ':self.df.loc['2SE','4/6Sr'],        
        '87Rb/86Sr':self.df.loc['Mean','7Rb/6Sr'],
        '2σ1':self.df.loc['2SE','7Rb/6Sr'],
        '87Sr/86Sr':self.df.loc['Mean','7/6Sr'],
        '2σ2':self.df.loc['2SE','7/6Sr']}
        result = pd.DataFrame(data = final,index = ['0'],columns = ['Sample','85Rb(v)','88Sr(v)','84Sr/86Sr','2σ','87Rb/86Sr','2σ1','87Sr/86Sr','2σ2'])
        return result