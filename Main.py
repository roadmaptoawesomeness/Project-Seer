# -*- coding: utf-8 -*-


from dask import delayed
import Forecast as f
import Optimize as o
import Sched as s

import pandas as pd


#Per ATM
def ATM_Main(series,val_dates,holidays,model):
    
    forecasts = f.forecast(series,val_dates,holidays,weekly=0,monthly=monthly,cpoint=cpoint)
    optimal  = o.optimize
        (b,d,reload_amt,
                 atm_no,days_no,reload_charge=2000, r=0.05/365,t=0,t_day0=0)
    
    decision = s.decision()
    
    
    return dataframme




#Error Check
def Check(date,holiday_file,model_file,atm_list="All",horizon=7,raw_path,out_path):
    
    
    #assumes same list of Holidays and Payrolls for all models
    
    sdate
    edate
    
    val_dates = pd.DataFrame(pd.date_range(start=sdate, end=edate),columns='ds')
    models = pd.read_csv(path+model_file, 
                            dtype={'TID':str,'Weekly':int,'Monthly':int})
    
    holidays = pd.read_csv(raw_path+'Holidays/'+holiday_file)
    train = pd.read_csv(raw_path+'Master/Train.csv')
    
    delayed(ed.forecast)(parameters)
    return None


date = "2020/01/01"
horizon = 14
atm_list=
    
    
    
