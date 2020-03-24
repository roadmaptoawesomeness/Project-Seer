# -*- coding: utf-8 -*-


from dask import delayed
import f_prophet as p
import f_optimize as o
import f_sched as s



#@delayed
def call_forecast(series,val_dates,holidays,model):
    ed.f(series,val_dates,holidays,weekly=0,monthly=monthly,cpoint=cpoint)
    

def call_optimize():


def call_sched():



def Main(date,horizon,atm_list,train_days,holiday_file,model_file,raw_path,out_path):

    
    #assumes same list of Holidays and Payrolls for all models
    holidays = pd.read_csv(raw_path+'Holidays/'+holiday_file)
    train = pd.
    
    delayed(ed.forecast)(parameters)
    
    
    
